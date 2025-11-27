import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

// 配置 dayjs 給 antd DatePicker 使用
import dayjs from 'dayjs'
import 'dayjs/locale/zh-tw'
import customParseFormat from 'dayjs/plugin/customParseFormat'
import weekday from 'dayjs/plugin/weekday'
import localeData from 'dayjs/plugin/localeData'
import weekOfYear from 'dayjs/plugin/weekOfYear'
import weekYear from 'dayjs/plugin/weekYear'
import advancedFormat from 'dayjs/plugin/advancedFormat'
import isSameOrBefore from 'dayjs/plugin/isSameOrBefore'
import isSameOrAfter from 'dayjs/plugin/isSameOrAfter'

dayjs.extend(customParseFormat)
dayjs.extend(weekday)
dayjs.extend(localeData)
dayjs.extend(weekOfYear)
dayjs.extend(weekYear)
dayjs.extend(advancedFormat)
dayjs.extend(isSameOrBefore)
dayjs.extend(isSameOrAfter)
dayjs.locale('zh-tw')

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)