import React, { useEffect, useState } from 'react'
import { api } from '../api'

export default function Void() {
  const [rows, setRows] = useState([])
  const [msg, setMsg] = useState('')
  const [err, setErr] = useState('')
  const load = async () => {
    const all = await api('/磅条')
    setRows(all.filter((r) => r.状态 === '待定级' || r.状态 === '待结价'))
  }
  useEffect(() => { load().catch((e) => setErr(e.message)) }, [])
  const cancel = async (id) => {
    setErr(''); setMsg('')
    try {
      const row = await api(`/销单/${id}`, { method: 'POST', body: '{}' })
      setMsg(`已销单 ${row.磅条号}`)
      await load()
    } catch (e) { setErr(e.message) }
  }
  return (
    <div className="panel">
      <h2>销单</h2>
      {msg && <div className="msg">{msg}</div>}
      {err && <div className="err">{err}</div>}
      <div className="table-wrap">
        <table>
          <thead><tr><th>磅条号</th><th>回收点</th><th>地磅</th><th>状态</th><th>净重</th><th>操作</th></tr></thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.编号}>
                <td>{r.磅条号}</td><td>{r.回收点}</td><td>{r.地磅}</td><td>{r.状态}</td><td>{r.净重}</td>
                <td><button type="button" onClick={() => cancel(r.编号)}>销单</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
