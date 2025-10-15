"""
排程資料庫服務
負責排程任務的資料庫操作
"""

import asyncio
import uuid
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, BigInteger, Boolean, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

# 資料庫配置
DATABASE_URL = "postgresql://postgres:password@postgres-db:5432/posting_management"

Base = declarative_base()

class ScheduleTask(Base):
    """排程任務資料表"""
    __tablename__ = "schedule_tasks"
    
    # 主鍵和時間戳
    schedule_id = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 基本資訊
    schedule_name = Column(String, nullable=False)
    schedule_description = Column(Text, nullable=True)
    session_id = Column(BigInteger, nullable=True)
    
    # 排程設定
    schedule_type = Column(String, nullable=False)  # 'immediate', '24hour_batch', '5min_batch', 'weekday_daily'
    status = Column(String, default='pending')  # 'pending', 'active', 'completed', 'failed', 'cancelled'
    # 自動發文開關
    auto_posting = Column(Boolean, default=False, nullable=False)
    
    # 時間設定
    interval_seconds = Column(Integer, default=30)
    batch_duration_hours = Column(Integer, nullable=True)
    daily_execution_time = Column(String, nullable=True)  # '09:00', '14:00' 等
    weekdays_only = Column(Boolean, default=True)
    timezone = Column(String, default='Asia/Taipei')
    
    # 執行控制
    max_posts_per_hour = Column(Integer, default=2)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    last_run = Column(DateTime, nullable=True)
    next_run = Column(DateTime, nullable=True)
    
    # 統計數據
    run_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    total_posts_generated = Column(Integer, default=0)
    
    # 生成配置
    generation_config = Column(JSON, nullable=True)
    batch_info = Column(JSON, nullable=True)
    
    # 錯誤處理
    error_message = Column(Text, nullable=True)
    
    # 關聯貼文
    generated_post_ids = Column(JSON, nullable=True)  # 存儲生成的貼文ID列表
    
    # 來源追蹤
    source_type = Column(String, nullable=True)  # 'batch_history' | 'self_learning'
    source_batch_id = Column(String, nullable=True)  # 批次歷史來源的批次ID
    source_experiment_id = Column(String, nullable=True)  # 自我學習來源的實驗ID
    source_feature_name = Column(String, nullable=True)  # 特徵名稱
    created_by = Column(String, default='system')  # 創建者

class SchedulePostRelation(Base):
    """排程與貼文關聯表"""
    __tablename__ = "schedule_post_relations"
    
    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(String, nullable=False, index=True)
    post_id = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 外鍵約束會在資料庫層面設定

class ScheduleDatabaseService:
    """排程資料庫服務"""
    
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_db_session(self) -> Session:
        """獲取資料庫會話"""
        return self.SessionLocal()
    
    def create_tables(self):
        """創建資料表"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("✅ 排程資料表創建成功")
        except Exception as e:
            logger.error(f"❌ 創建排程資料表失敗: {e}")
            raise
    
    async def create_schedule_task(self, 
                                 schedule_name: str,
                                 schedule_description: Optional[str] = None,
                                 session_id: Optional[int] = None,
                                 schedule_type: str = 'immediate',
                                 interval_seconds: int = 30,
                                 batch_duration_hours: Optional[int] = None,
                                 daily_execution_time: Optional[str] = None,
                                 weekdays_only: bool = True,
                                 max_posts_per_hour: int = 2,
                                 timezone: str = 'Asia/Taipei',
                                 generation_config: Optional[Dict[str, Any]] = None,
                                 batch_info: Optional[Dict[str, Any]] = None,
                                 auto_posting: bool = False,
                                 # 來源追蹤參數
                                 source_type: Optional[str] = None,
                                 source_batch_id: Optional[str] = None,
                                 source_experiment_id: Optional[str] = None,
                                 source_feature_name: Optional[str] = None,
                                 created_by: str = 'system') -> str:
        """創建排程任務"""
        schedule_id = str(uuid.uuid4())
        
        db = self.get_db_session()
        try:
            schedule_task = ScheduleTask(
                schedule_id=schedule_id,
                schedule_name=schedule_name,
                schedule_description=schedule_description,
                session_id=session_id,
                schedule_type=schedule_type,
                interval_seconds=interval_seconds,
                batch_duration_hours=batch_duration_hours,
                daily_execution_time=daily_execution_time,
                weekdays_only=weekdays_only,
                max_posts_per_hour=max_posts_per_hour,
                timezone=timezone,
                generation_config=generation_config or {},
                batch_info=batch_info or {},
                auto_posting=auto_posting,
                # 來源追蹤
                source_type=source_type,
                source_batch_id=source_batch_id,
                source_experiment_id=source_experiment_id,
                source_feature_name=source_feature_name,
                created_by=created_by
            )
            
            db.add(schedule_task)
            db.commit()
            db.refresh(schedule_task)
            
            logger.info(f"✅ 排程任務創建成功 - Schedule ID: {schedule_id}")
            return schedule_id
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ 創建排程任務失敗: {e}")
            raise
        finally:
            db.close()
    
    def _generate_schedule_name(self, schedule_data: Dict[str, Any]) -> str:
        """生成直觀的排程名稱"""
        try:
            schedule_type = schedule_data.get('schedule_type', 'unknown')
            daily_execution_time = schedule_data.get('daily_execution_time', '')
            source_type = schedule_data.get('source_type', '')
            source_feature_name = schedule_data.get('source_feature_name', '')
            
            # 根據排程類型生成名稱
            if schedule_type == 'weekday_daily':
                if daily_execution_time:
                    return f"每日排程_{daily_execution_time}"
                else:
                    return "每日排程"
            elif schedule_type == 'immediate':
                return "立即執行"
            elif schedule_type == '24hour_batch':
                return "24小時批次"
            elif schedule_type == '5min_batch':
                return "5分鐘批次"
            else:
                # 根據來源類型生成名稱
                if source_type == 'self_learning':
                    if source_feature_name:
                        return f"自我學習_{source_feature_name}"
                    else:
                        return "自我學習實驗"
                elif source_type == 'batch_history':
                    return "批次歷史排程"
                else:
                    return f"排程_{schedule_type}"
        except Exception as e:
            logger.error(f"❌ 生成排程名稱失敗: {e}")
            return f"排程_{schedule_data.get('schedule_type', 'unknown')}"
    
    async def get_active_schedule_tasks(self) -> List[Dict[str, Any]]:
        """獲取所有 active 排程任務"""
        db = self.get_db_session()
        try:
            from sqlalchemy import text
            
            query = text("""
                SELECT schedule_id, schedule_name, schedule_description, 
                       daily_execution_time, schedule_type, status, 
                       interval_seconds, batch_duration_hours, weekdays_only,
                       timezone, max_posts_per_hour, created_at, updated_at,
                       started_at, completed_at, last_run, next_run,
                       generation_config
                FROM schedule_tasks
                WHERE status = 'active'
                ORDER BY created_at DESC
            """)
            
            result = db.execute(query)
            tasks = result.fetchall()
            
            # 轉換為字典格式
            active_tasks = []
            for task in tasks:
                active_tasks.append({
                    "schedule_id": task[0],
                    "schedule_name": task[1],
                    "schedule_description": task[2],
                    "daily_execution_time": task[3],
                    "schedule_type": task[4],
                    "status": task[5],
                    "interval_seconds": task[6],
                    "batch_duration_hours": task[7],
                    "weekdays_only": task[8],
                    "timezone": task[9],
                    "max_posts_per_hour": task[10],
                    "created_at": task[11],
                    "updated_at": task[12],
                    "started_at": task[13],
                    "completed_at": task[14],
                    "last_run": task[15],
                    "next_run": task[16],
                    "generation_config": task[17] or {}
                })
            
            return active_tasks
            
        except Exception as e:
            logger.error(f"❌ 獲取 active 排程任務失敗: {e}")
            return []
        finally:
            db.close()
    
    async def update_schedule_next_run(self, schedule_id: str, next_run: datetime):
        """更新排程的下次執行時間"""
        db = self.get_db_session()
        try:
            from sqlalchemy import text
            
            # 移除時區信息，保留台北時間的數值
            # 因為資料庫欄位是 timestamp without time zone
            if next_run.tzinfo is not None:
                next_run_naive = next_run.replace(tzinfo=None)
            else:
                next_run_naive = next_run
            
            query = text("""
                UPDATE schedule_tasks 
                SET next_run = :next_run, updated_at = :updated_at
                WHERE schedule_id = :schedule_id
            """)
            
            db.execute(query, {
                'schedule_id': schedule_id,
                'next_run': next_run_naive,  # 使用 naive datetime
                'updated_at': datetime.utcnow()
            })
            db.commit()
            
            logger.info(f"✅ 更新排程下次執行時間成功 - Schedule ID: {schedule_id}, Next Run: {next_run_naive} (台北時間)")
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ 更新排程下次執行時間失敗: {e}")
            raise
        finally:
            db.close()
    
    async def get_schedule_task(self, schedule_id: str) -> Optional[Dict[str, Any]]:
        """獲取排程任務"""
        db = self.get_db_session()
        try:
            task = db.query(ScheduleTask).filter(ScheduleTask.schedule_id == schedule_id).first()
            if not task:
                return None
            
            return {
                'schedule_id': task.schedule_id,
                'schedule_name': task.schedule_name,
                'schedule_description': task.schedule_description,
                'session_id': task.session_id,
                'schedule_type': task.schedule_type,
                'status': task.status,
                'auto_posting': task.auto_posting,
                'interval_seconds': task.interval_seconds,
                'batch_duration_hours': task.batch_duration_hours,
                'daily_execution_time': task.daily_execution_time,
                'weekdays_only': task.weekdays_only,
                'timezone': task.timezone,
                'max_posts_per_hour': task.max_posts_per_hour,
                'started_at': task.started_at.isoformat() if task.started_at else None,
                'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                'last_run': task.last_run.isoformat() if task.last_run else None,
                'next_run': task.next_run.isoformat() if task.next_run else None,
                'run_count': task.run_count,
                'success_count': task.success_count,
                'failure_count': task.failure_count,
                'total_posts_generated': task.total_posts_generated,
                'generation_config': task.generation_config,
                'batch_info': task.batch_info,
                'error_message': task.error_message,
                'generated_post_ids': task.generated_post_ids,
                'created_at': task.created_at.isoformat(),
                'updated_at': task.updated_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 獲取排程任務失敗: {e}")
            raise
        finally:
            db.close()
    
    async def get_all_schedule_tasks(self) -> List[Dict[str, Any]]:
        """獲取所有排程任務"""
        db = self.get_db_session()
        try:
            tasks = db.query(ScheduleTask).order_by(ScheduleTask.created_at.desc()).all()
            result = []
            for task in tasks:
                task_dict = await self.get_schedule_task(task.schedule_id)
                if task_dict:
                    result.append(task_dict)
            return result
            
        except Exception as e:
            logger.error(f"❌ 獲取所有排程任務失敗: {e}")
            raise
        finally:
            db.close()
    
    async def update_schedule_status(self, schedule_id: str, status: str, 
                                   error_message: Optional[str] = None,
                                   started_at: Optional[datetime] = None,
                                   completed_at: Optional[datetime] = None,
                                   last_run: Optional[datetime] = None,
                                   next_run: Optional[datetime] = None) -> bool:
        """更新排程狀態"""
        db = self.get_db_session()
        try:
            task = db.query(ScheduleTask).filter(ScheduleTask.schedule_id == schedule_id).first()
            if not task:
                logger.error(f"❌ 排程任務不存在: {schedule_id}")
                return False
            
            task.status = status
            task.updated_at = datetime.utcnow()
            
            if error_message:
                task.error_message = error_message
            if started_at:
                task.started_at = started_at
            if completed_at:
                task.completed_at = completed_at
            if last_run:
                task.last_run = last_run
            if next_run:
                task.next_run = next_run
            
            db.commit()
            logger.info(f"✅ 排程狀態更新成功: {schedule_id} -> {status}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ 更新排程狀態失敗: {e}")
            return False
        finally:
            db.close()
    
    async def increment_schedule_stats(self, schedule_id: str, 
                                     run_count: int = 0,
                                     success_count: int = 0,
                                     failure_count: int = 0,
                                     posts_generated: int = 0) -> bool:
        """增加排程統計數據"""
        db = self.get_db_session()
        try:
            task = db.query(ScheduleTask).filter(ScheduleTask.schedule_id == schedule_id).first()
            if not task:
                logger.error(f"❌ 排程任務不存在: {schedule_id}")
                return False
            
            task.run_count = (task.run_count or 0) + run_count
            task.success_count = (task.success_count or 0) + success_count
            task.failure_count = (task.failure_count or 0) + failure_count
            task.total_posts_generated = (task.total_posts_generated or 0) + posts_generated
            task.updated_at = datetime.utcnow()
            
            db.commit()
            logger.info(f"✅ 排程統計更新成功: {schedule_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ 更新排程統計失敗: {e}")
            return False
        finally:
            db.close()
    
    async def add_generated_post(self, schedule_id: str, post_id: str) -> bool:
        """添加生成的貼文到排程"""
        db = self.get_db_session()
        try:
            # 更新排程任務的 generated_post_ids
            task = db.query(ScheduleTask).filter(ScheduleTask.schedule_id == schedule_id).first()
            if not task:
                logger.error(f"❌ 排程任務不存在: {schedule_id}")
                return False
            
            # 更新 JSON 欄位
            current_posts = task.generated_post_ids or []
            if post_id not in current_posts:
                current_posts.append(post_id)
                task.generated_post_ids = current_posts
                task.updated_at = datetime.utcnow()
            
            # 創建關聯記錄
            relation = SchedulePostRelation(
                schedule_id=schedule_id,
                post_id=post_id
            )
            db.add(relation)
            
            db.commit()
            logger.info(f"✅ 貼文關聯添加成功: {schedule_id} -> {post_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ 添加貼文關聯失敗: {e}")
            return False
        finally:
            db.close()
    
    async def get_schedule_posts(self, schedule_id: str) -> List[str]:
        """獲取排程生成的所有貼文ID"""
        db = self.get_db_session()
        try:
            relations = db.query(SchedulePostRelation).filter(
                SchedulePostRelation.schedule_id == schedule_id
            ).all()
            
            return [relation.post_id for relation in relations]
            
        except Exception as e:
            logger.error(f"❌ 獲取排程貼文失敗: {e}")
            return []
        finally:
            db.close()
    
    async def get_post_schedule(self, post_id: str) -> Optional[str]:
        """獲取貼文所屬的排程ID"""
        db = self.get_db_session()
        try:
            relation = db.query(SchedulePostRelation).filter(
                SchedulePostRelation.post_id == post_id
            ).first()
            
            return relation.schedule_id if relation else None
            
        except Exception as e:
            logger.error(f"❌ 獲取貼文排程失敗: {e}")
            return None
        finally:
            db.close()
    
    async def cancel_schedule_task(self, schedule_id: str) -> bool:
        """取消排程任務"""
        return await self.update_schedule_status(schedule_id, 'cancelled')
    
    async def delete_schedule_task(self, schedule_id: str) -> bool:
        """刪除排程任務"""
        db = self.get_db_session()
        try:
            # 先刪除關聯記錄
            db.query(SchedulePostRelation).filter(
                SchedulePostRelation.schedule_id == schedule_id
            ).delete()
            
            # 再刪除排程任務
            result = db.query(ScheduleTask).filter(
                ScheduleTask.schedule_id == schedule_id
            ).delete()
            
            db.commit()
            
            if result > 0:
                logger.info(f"✅ 排程任務刪除成功: {schedule_id}")
                return True
            else:
                logger.warning(f"⚠️ 排程任務不存在: {schedule_id}")
                return False
                
        except Exception as e:
            db.rollback()
            logger.error(f"❌ 刪除排程任務失敗: {e}")
            return False
        finally:
            db.close()

# 全局排程資料庫服務實例
schedule_db_service = ScheduleDatabaseService()
