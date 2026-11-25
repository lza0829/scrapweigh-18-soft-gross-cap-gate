import React, { useEffect, useState } from 'react'
import { api } from '../api'

export default function Grade() {
  const [rows, setRows] = useState([])
  const [grades, setGrades] = useState([])
  const [ticketId, setTicketId] = useState('')
  const [gradeId, setGradeId] = useState('')
  const [msg, setMsg] = useState('')
  const [err, setErr] = useState('')
  const load = async () => {
    const [t, g] = await Promise.all([api('/磅条?状态=' + encodeURIComponent('待定级')), api('/品级')])
    setRows(t)
    setGrades(g)
    if (!ticketId && t[0]) setTicketId(String(t[0].编号))
    if (!gradeId && g[0]) setGradeId(String(g[0].编号))
  }
  useEffect(() => { load().catch((e) => setErr(e.message)) }, [])
  const lock = async () => {
    setErr(''); setMsg('')
    try {
      const row = await api(`/定级/${ticketId}`, {
        method: 'POST',
        body: JSON.stringify({ 品级编号: Number(gradeId) }),
      })
      setMsg(`已锁价 ${row.磅条号}，单价 ${row.锁价}`)
      setTicketId('')
      await load()
    } catch (e) { setErr(e.message) }
  }
  return (
    <div className="panel">
      <h2>定级</h2>
      <div className="row">
        <label>待定级磅条
          <select value={ticketId} onChange={(e) => setTicketId(e.target.value)}>
            <option value="">请选择</option>
            {rows.map((r) => (
              <option key={r.编号} value={r.编号}>{r.磅条号} · {r.地磅} · 净重 {r.净重}</option>
            ))}
          </select>
        </label>
        <label>品级
          <select value={gradeId} onChange={(e) => setGradeId(e.target.value)}>
            {grades.map((g) => (
              <option key={g.编号} value={g.编号}>{g.品类} {g.品级名} · {g.单价}</option>
            ))}
          </select>
        </label>
        <button type="button" onClick={lock} disabled={!ticketId || !gradeId}>锁价</button>
      </div>
      {msg && <div className="msg">{msg}</div>}
      {err && <div className="err">{err}</div>}
      <div className="table-wrap">
        <table>
          <thead><tr><th>磅条号</th><th>回收点</th><th>地磅</th><th>净重</th><th>状态</th></tr></thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.编号}><td>{r.磅条号}</td><td>{r.回收点}</td><td>{r.地磅}</td><td>{r.净重}</td><td>{r.状态}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
