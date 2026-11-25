import React, { useEffect, useState } from 'react'
import { api } from '../api'

export default function Settle() {
  const [rows, setRows] = useState([])
  const [msg, setMsg] = useState('')
  const [err, setErr] = useState('')
  const load = () => api('/磅条?状态=' + encodeURIComponent('待结价')).then(setRows).catch((e) => setErr(e.message))
  useEffect(() => { load() }, [])
  const settle = async (id) => {
    setErr(''); setMsg('')
    try {
      const row = await api(`/结价/${id}`, { method: 'POST', body: '{}' })
      setMsg(`已结价 ${row.磅条号}，金额 ${row.金额}，地磅已空闲`)
      await load()
    } catch (e) { setErr(e.message) }
  }
  return (
    <div className="panel">
      <h2>结价</h2>
      {msg && <div className="msg">{msg}</div>}
      {err && <div className="err">{err}</div>}
      <div className="table-wrap">
        <table>
          <thead><tr><th>磅条号</th><th>地磅</th><th>品级</th><th>净重</th><th>锁价</th><th>应付</th><th>操作</th></tr></thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.编号}>
                <td>{r.磅条号}</td><td>{r.地磅}</td><td>{r.品类}{r.品级}</td>
                <td>{r.净重}</td><td>{r.锁价}</td>
                <td>{r.锁价 != null ? (Number(r.净重) * Number(r.锁价)).toFixed(2) : '-'}</td>
                <td><button type="button" onClick={() => settle(r.编号)}>结价</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
