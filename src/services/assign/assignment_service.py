"""
話題派發服務
負責將話題派發給適合的 KOL，並處理去重邏輯
"""
import logging
from typing import List, Dict, Any, Set, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid

# 導入話題分類服務
from src.services.classification.topic_classifier import create_topic_classifier, TopicClassification

logger = logging.getLogger(__name__)


@dataclass
class KOLProfile:
    """KOL 配置資料"""
    serial: int
    nickname: str
    email: str
    password: str
    member_id: str
    persona: str
    status: str
    topic_preferences: List[str] = field(default_factory=list)
    forbidden_categories: List[str] = field(default_factory=list)
    data_preferences: List[str] = field(default_factory=list)
    enabled: bool = True


@dataclass
class TopicData:
    """話題資料"""
    topic_id: str
    title: str
    input_index: int
    persona_tags: List[str] = field(default_factory=list)
    industry_tags: List[str] = field(default_factory=list)
    event_tags: List[str] = field(default_factory=list)
    stock_tags: List[str] = field(default_factory=list)
    horizon: Optional[str] = None
    stocks: List[Dict[str, str]] = field(default_factory=list)
    primary_stock: Optional[Dict[str, str]] = None
    top3: List[Dict[str, Any]] = field(default_factory=list)
    assign_to: Optional[int] = None
    classification: Optional[TopicClassification] = None  # 分類結果


@dataclass
class TaskAssignment:
    """任務派發結果"""
    task_id: str  # 格式: topic_id::kol_serial
    topic_id: str
    kol_serial: int
    topic_title: str
    topic_keywords: List[str]
    match_score: float
    status: str = "queued"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class AssignmentService:
    """話題派發服務"""
    
    def __init__(self, sheets_client, use_double_colon: bool = True):
        """
        初始化派發服務
        
        Args:
            sheets_client: Google Sheets 客戶端
            use_double_colon: 是否使用 :: 格式的貼文ID (True) 或 - 格式 (False)
        """
        self.sheets_client = sheets_client
        self.use_double_colon = use_double_colon
        self._kol_profiles: List[KOLProfile] = []
        self._existing_tasks: Set[str] = set()
        self._topic_classifier = create_topic_classifier()  # 初始化話題分類器
    
    def classify_topic(self, topic_id: str, title: str, content: str) -> TopicClassification:
        """
        對話題進行分類
        
        Args:
            topic_id: 話題ID
            title: 話題標題
            content: 話題內容
            
        Returns:
            分類結果
        """
        return self._topic_classifier.classify_topic(topic_id, title, content)
    
    def _make_task_id(self, topic_id: str, kol_serial: int) -> str:
        """
        生成任務ID
        
        Args:
            topic_id: 話題ID
            kol_serial: KOL序號
            
        Returns:
            任務ID
        """
        separator = "::" if self.use_double_colon else "-"
        return f"{topic_id}{separator}{kol_serial}"
    
    def _parse_task_id(self, task_id: str) -> tuple[str, int]:
        """
        解析任務ID
        
        Args:
            task_id: 任務ID
            
        Returns:
            (topic_id, kol_serial)
        """
        # 支援兩種格式: topic_id::serial 和 topic_id-serial
        if "::" in task_id:
            parts = task_id.split("::")
        elif "-" in task_id:
            # 需要小心處理，因為 topic_id 本身可能包含 -
            # 假設最後一個 - 後面是序號
            parts = task_id.rsplit("-", 1)
        else:
            raise ValueError(f"無法解析任務ID: {task_id}")
        
        if len(parts) != 2:
            raise ValueError(f"無法解析任務ID: {task_id}")
        
        try:
            topic_id = parts[0]
            kol_serial = int(parts[1])
            return topic_id, kol_serial
        except ValueError:
            raise ValueError(f"無法解析任務ID: {task_id}")
    
    def load_kol_profiles(self) -> None:
        """從 Google Sheets 載入 KOL 配置"""
        try:
            logger.info("載入 KOL 配置...")
            
            # 讀取 KOL 數據
            data = self.sheets_client.read_sheet('同學會帳號管理')
            
            if not data or len(data) < 2:
                logger.warning("沒有找到 KOL 配置數據")
                return
            
            headers = data[0]
            rows = data[1:]
            
            # 建立欄位索引映射
            field_map = {}
            for i, header in enumerate(headers):
                if '序號' in header:
                    field_map['serial'] = i
                elif '暱稱' in header:
                    field_map['nickname'] = i
                elif 'Email' in header or '帳號' in header:
                    field_map['email'] = i
                elif '密碼' in header:
                    field_map['password'] = i
                elif 'MemberId' in header:
                    field_map['member_id'] = i
                elif '人設' in header:
                    field_map['persona'] = i
                elif '狀態' in header and i < 20:  # 限制在前20欄內
                    field_map['status'] = i
                elif 'Topic偏好類別' in header:
                    field_map['topic_preferences'] = i
                elif '禁講類別' in header:
                    field_map['forbidden_categories'] = i
                elif '資料偏好' in header:
                    field_map['data_preferences'] = i
            
            logger.info(f"欄位映射: {field_map}")
            
            # 解析 KOL 資料
            kol_profiles = []
            for row in rows:
                if len(row) <= max(field_map.values(), default=0):
                    continue
                
                try:
                    # 基本欄位
                    serial = int(row[field_map['serial']]) if 'serial' in field_map and row[field_map['serial']] else 0
                    nickname = row[field_map['nickname']] if 'nickname' in field_map else ""
                    email = row[field_map['email']] if 'email' in field_map else ""
                    password = row[field_map['password']] if 'password' in field_map else ""
                    member_id = row[field_map['member_id']] if 'member_id' in field_map else ""
                    persona = row[field_map['persona']] if 'persona' in field_map else ""
                    status = row[field_map['status']] if 'status' in field_map else "active"
                    
                    # 解析列表欄位
                    def parse_list_field(field_name: str) -> List[str]:
                        if field_name not in field_map:
                            return []
                        value = row[field_map[field_name]]
                        if not value:
                            return []
                        return [item.strip() for item in value.split(',') if item.strip()]
                    
                    topic_preferences = parse_list_field('topic_preferences')
                    forbidden_categories = parse_list_field('forbidden_categories')
                    data_preferences = parse_list_field('data_preferences')
                    
                    # 檢查是否啟用
                    enabled = status.lower() == "active"
                    
                    if serial and nickname and email:
                        profile = KOLProfile(
                            serial=serial,
                            nickname=nickname,
                            email=email,
                            password=password,
                            member_id=member_id,
                            persona=persona,
                            status=status,
                            topic_preferences=topic_preferences,
                            forbidden_categories=forbidden_categories,
                            data_preferences=data_preferences,
                            enabled=enabled
                        )
                        kol_profiles.append(profile)
                        
                except (ValueError, IndexError) as e:
                    logger.warning(f"跳過無效的 KOL 資料行: {e}")
                    continue
            
            self._kol_profiles = kol_profiles
            logger.info(f"成功載入 {len(kol_profiles)} 個 KOL 配置")
            
        except Exception as e:
            logger.error(f"載入 KOL 配置失敗: {e}")
            raise
    
    def load_existing_tasks(self) -> None:
        """從 Google Sheets 載入現有任務"""
        try:
            logger.info("載入現有任務...")
            
            # 讀取任務數據
            data = self.sheets_client.read_sheet('貼文記錄表')
            
            if not data or len(data) < 2:
                logger.info("沒有找到現有任務")
                return
            
            headers = data[0]
            rows = data[1:]
            
            # 查找貼文ID欄位
            post_id_column = None
            for i, header in enumerate(headers):
                if '貼文ID' in header:
                    post_id_column = i
                    break
            
            if post_id_column is None:
                logger.warning("找不到貼文ID欄位")
                return
            
            # 提取現有任務ID
            existing_tasks = set()
            for row in rows:
                if len(row) > post_id_column and row[post_id_column]:
                    task_id = row[post_id_column].strip()
                    if task_id:
                        # 正規化任務ID格式
                        try:
                            topic_id, kol_serial = self._parse_task_id(task_id)
                            normalized_id = self._make_task_id(topic_id, kol_serial)
                            existing_tasks.add(normalized_id)
                        except ValueError:
                            logger.warning(f"無法解析任務ID: {task_id}")
                            # 直接加入原始ID作為備用
                            existing_tasks.add(task_id)
            
            self._existing_tasks = existing_tasks
            logger.info(f"成功載入 {len(existing_tasks)} 個現有任務")
            
        except Exception as e:
            logger.error(f"載入現有任務失敗: {e}")
            raise
    
    def calculate_match_score(self, topic: TopicData, kol: KOLProfile) -> float:
        """
        計算話題與 KOL 的匹配分數
        
        Args:
            topic: 話題資料
            kol: KOL配置
            
        Returns:
            匹配分數 (0.0 - 10.0)
        """
        score = 0.0
        
        # 檢查禁講類別 (強制排除)
        all_topic_tags = topic.persona_tags + topic.industry_tags + topic.event_tags + topic.stock_tags
        if any(tag in kol.forbidden_categories for tag in all_topic_tags):
            return -1000.0  # 強制排除
        
        # 人設匹配 (權重 1.5)
        if kol.persona in topic.persona_tags:
            score += 1.5
        
        # Topic偏好匹配 (權重 1.2)
        topic_pref_matches = len(set(topic.industry_tags + topic.event_tags + topic.stock_tags) & set(kol.topic_preferences))
        score += topic_pref_matches * 1.2
        
        # 資料偏好匹配 (權重 0.5-0.8)
        if 'ohlc' in kol.data_preferences and ('技術派' in topic.persona_tags or '技術面' in topic.event_tags):
            score += 0.5
        if 'revenue' in kol.data_preferences and '月營收' in topic.event_tags:
            score += 0.8
        if 'fundamental' in kol.data_preferences and '財報' in topic.event_tags:
            score += 0.8
        
        return round(score, 2)
    
    def assign_topics(self, topics: List[TopicData], max_assignments_per_topic: int = 3) -> List[TaskAssignment]:
        """
        派發話題給 KOL
        
        Args:
            topics: 話題列表
            max_assignments_per_topic: 每個話題最多派發給幾個KOL
            
        Returns:
            任務派發結果列表
        """
        try:
            # 確保已載入 KOL 配置和現有任務
            if not self._kol_profiles:
                self.load_kol_profiles()
            
            if not self._existing_tasks:
                self.load_existing_tasks()
            
            logger.info(f"開始派發 {len(topics)} 個話題...")
            
            assignments = []
            
            for topic in topics:
                logger.info(f"處理話題: {topic.title}")
                
                # 計算所有 KOL 的匹配分數
                kol_scores = []
                for kol in self._kol_profiles:
                    if not kol.enabled:
                        continue
                    
                    score = self.calculate_match_score(topic, kol)
                    if score > -999:  # 排除被禁講的KOL
                        kol_scores.append({
                            'kol': kol,
                            'score': score
                        })
                
                # 排序並選擇最佳匹配
                kol_scores.sort(key=lambda x: x['score'], reverse=True)
                
                # 取 top3 或指定數量
                selected_kols = kol_scores[:max_assignments_per_topic]
                
                # 如果話題有指定 assign_to，優先使用
                if topic.assign_to:
                    # 查找指定的 KOL
                    assigned_kol = next((kol for kol in self._kol_profiles if kol.serial == topic.assign_to), None)
                    if assigned_kol and assigned_kol.enabled:
                        # 將指定的 KOL 放到最前面
                        selected_kols = [{'kol': assigned_kol, 'score': 999.0}] + \
                                      [item for item in selected_kols if item['kol'].serial != topic.assign_to]
                
                # 生成任務派發
                topic_assignments = 0
                for item in selected_kols:
                    if topic_assignments >= max_assignments_per_topic:
                        break
                    
                    kol = item['kol']
                    score = item['score']
                    
                    # 檢查是否已存在
                    task_id = self._make_task_id(topic.topic_id, kol.serial)
                    if task_id in self._existing_tasks:
                        logger.info(f"任務已存在，跳過: {task_id}")
                        continue
                    
                    # 創建新任務
                    assignment = TaskAssignment(
                        task_id=task_id,
                        topic_id=topic.topic_id,
                        kol_serial=kol.serial,
                        topic_title=topic.title,
                        topic_keywords=topic.persona_tags + topic.industry_tags + topic.event_tags,
                        match_score=score
                    )
                    
                    assignments.append(assignment)
                    self._existing_tasks.add(task_id)  # 避免同批次重複
                    topic_assignments += 1
                    
                    logger.info(f"派發任務: {topic.title} -> {kol.nickname} (分數: {score})")
            
            logger.info(f"派發完成，共產生 {len(assignments)} 個新任務")
            return assignments
            
        except Exception as e:
            logger.error(f"話題派發失敗: {e}")
            raise


# 測試函數
def test_assignment_service():
    """測試派發服務"""
    try:
        from clients.google.sheets_client import GoogleSheetsClient
        
        # 創建 Google Sheets 客戶端
        sheets_client = GoogleSheetsClient(
            credentials_file="./credentials/google-service-account.json",
            spreadsheet_id="148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
        )
        
        # 創建派發服務
        service = AssignmentService(sheets_client, use_double_colon=True)
        
        # 載入配置
        service.load_kol_profiles()
        service.load_existing_tasks()
        
        print(f"✅ 載入了 {len(service._kol_profiles)} 個 KOL")
        print(f"✅ 載入了 {len(service._existing_tasks)} 個現有任務")
        
        # 創建測試話題
        test_topic = TopicData(
            topic_id=str(uuid.uuid4()),
            title="台積電技術面分析",
            input_index=0,
            persona_tags=["技術派"],
            industry_tags=["半導體"],
            event_tags=["技術分析"],
            stocks=[{"name_zh": "台積電", "stock_id": "2330"}],
            primary_stock={"name_zh": "台積電", "stock_id": "2330"}
        )
        
        # 測試派發
        assignments = service.assign_topics([test_topic], max_assignments_per_topic=3)
        
        print(f"✅ 成功派發 {len(assignments)} 個任務")
        for assignment in assignments:
            print(f"   {assignment.task_id} -> 分數: {assignment.match_score}")
        
        return True
        
    except Exception as e:
        print(f"❌ 派發服務測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_assignment_service()
