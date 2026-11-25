import React, { useEffect, useState } from 'react'
import { api } from '../api'

export default function Shifts() {
  const [rows, setRows] = useState([])
  const [day, setDay] = useState('')
  const [name, setName] = useState('晚班')
  const [err, setErr] = useState('')
  const [msg, setMsg] = useState('')
  const load = () => api('/班次').then(setRows).catch((e) => setErr(e.message))
  useEffect(() => {
    const d = new Date()
    const m = String(d.getMonth() + 1).padStart(2, '0')
    const dd = String(d.getDate()).padStart(2, '0')
    setDay(`${d.getFullYear()}-${m}-${dd}`)
    load()
  }, [])
  const stamp = async (id) => {
    setErr(''); setMsg('')
    try {
      await api(`/班次/${id}/落印`, { method: 'POST', body: '{}' })
      setMsg('已落印')
      await load()
    } catch (e) { setErr(e.message) }
  }
  const open = async () => {
    setErr(''); setMsg('')
    try {
      await api('/班次', { method: 'POST', body: JSON.stringify({ 营业日: day, 班次名: name }) })
      setMsg('已开班')
      await load()
    } catch (e) { setErr(e.message) }
  }
  return (
    <div className="panel">
      <h2>班次</h2>
      <div className="row">
        <label>营业日<input value={day} onChange={(e) => setDay(e.target.value)} /></label>
        <label>班次名<input value={name} onChange={(e) => setName(e.target.value)} /></label>
        <button type="button" onClick={open}>开班</button>
      </div>
      {msg && <div className="msg">{msg}</div>}
      {err && <div className="err">{err}</div>}
      <table>
        <thead><tr><th>营业日</th><th>班次</th><th>状态</th><th>落印时间</th><th>操作</th></tr></thead>
        <tbody>
          {rows.map((s) => (
            <tr key={s.编号}>
              <td>{s.营业日}</td><td>{s.班次名}</td><td>{s.状态}</td><td>{s.落印时间 || '-'}</td>
              <td>{s.状态 === '未落印' && <button type="button" onClick={() => stamp(s.编号)}>落印</button>}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
