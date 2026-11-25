import React, { useEffect, useState } from 'react'
import { api } from '../api'

const STATUSES = ['营业中', '停收', '已注销']

export default function Sites() {
  const [rows, setRows] = useState([])
  const [name, setName] = useState('')
  const [addr, setAddr] = useState('')
  const [err, setErr] = useState('')
  const [msg, setMsg] = useState('')
  const load = () => api('/回收点').then(setRows).catch((e) => setErr(e.message))
  useEffect(() => { load() }, [])
  const create = async () => {
    setErr(''); setMsg('')
    try {
      await api('/回收点', { method: 'POST', body: JSON.stringify({ 名称: name, 地址: addr }) })
      setName(''); setAddr(''); setMsg('回收点已新增')
      await load()
    } catch (e) { setErr(e.message) }
  }
  const setStatus = async (id, status) => {
    setErr(''); setMsg('')
    try {
      await api(`/回收点/${id}/状态`, { method: 'POST', body: JSON.stringify({ 状态: status }) })
      setMsg('回收点状态已更新')
      await load()
    } catch (e) { setErr(e.message) }
  }
  return (
    <div className="panel">
      <h2>回收点</h2>
      <div className="row">
        <label>名称<input value={name} onChange={(e) => setName(e.target.value)} /></label>
        <label>地址<input value={addr} onChange={(e) => setAddr(e.target.value)} /></label>
        <button type="button" onClick={create}>新增</button>
      </div>
      {msg && <div className="msg">{msg}</div>}
      {err && <div className="err">{err}</div>}
      <table>
        <thead><tr><th>名称</th><th>状态</th><th>地址</th><th>操作</th></tr></thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.编号}>
              <td>{r.名称}</td><td>{r.状态}</td><td>{r.地址 || '-'}</td>
              <td>
                {STATUSES.filter((s) => s !== r.状态).map((s) => (
                  <button key={s} type="button" className="secondary" onClick={() => setStatus(r.编号, s)}>{s}</button>
                ))}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
