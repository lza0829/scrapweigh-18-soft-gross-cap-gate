import React from 'react'
import { NavLink, Route, Routes } from 'react-router-dom'
import Overview from './pages/Overview'
import Weigh from './pages/Weigh'
import Tickets from './pages/Tickets'
import Grade from './pages/Grade'
import Settle from './pages/Settle'
import Void from './pages/Void'
import Scales from './pages/Scales'
import Grades from './pages/Grades'
import Shifts from './pages/Shifts'
import Sites from './pages/Sites'
import Settings from './pages/Settings'
import Audit from './pages/Audit'

const links = [
  ['/', '总览'],
  ['/过磅', '过磅'],
  ['/磅条', '磅条'],
  ['/定级', '定级'],
  ['/结价', '结价'],
  ['/销单', '销单'],
  ['/地磅', '地磅'],
  ['/品级', '品级'],
  ['/班次', '班次'],
  ['/回收点', '回收点'],
  ['/设置', '设置'],
  ['/审计', '审计'],
]

export default function App() {
  return (
    <div className="shell">
      <header className="topbar">
        <div>
          <div className="brand">旧物磅条</div>
          <div className="brand-sub">过磅入站 · 品级锁价 · 结算关账 · 班次落印</div>
        </div>
        <nav className="nav">
          {links.map(([to, label]) => (
            <NavLink key={to} to={to} end={to === '/'} className={({ isActive }) => (isActive ? 'active' : '')}>
              {label}
            </NavLink>
          ))}
        </nav>
      </header>
      <main className="main">
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/过磅" element={<Weigh />} />
          <Route path="/磅条" element={<Tickets />} />
          <Route path="/定级" element={<Grade />} />
          <Route path="/结价" element={<Settle />} />
          <Route path="/销单" element={<Void />} />
          <Route path="/地磅" element={<Scales />} />
          <Route path="/品级" element={<Grades />} />
          <Route path="/班次" element={<Shifts />} />
          <Route path="/回收点" element={<Sites />} />
          <Route path="/设置" element={<Settings />} />
          <Route path="/审计" element={<Audit />} />
        </Routes>
      </main>
    </div>
  )
}
