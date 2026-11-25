import React, { useEffect, useState } from 'react'
import { api } from '../api'

export default function Scales() {
  const [rows, setRows] = useState([])
  const [sites, setSites] = useState([])
  const [siteId, setSiteId] = useState('')
  const [code, setCode] = useState('')
  const [err, setErr] = useState('')
  const [msg, setMsg] = useState('')
  const load = async () => {
    const [sc, st] = await Promise.all([api('/地磅'), api('/回收点')])
    setRows(sc)
    setSites(st.filter((s) => s.状态 !== '已注销'))
    if (!siteId && st[0]) setSiteId(String(st[0].编号))
  }
  useEffect(() => { load().catch((e) => setErr(e.message)) }, [])
  const setStatus = async (id, status) => {
    setErr(''); setMsg('')
    try {
      await api(`/地磅/${id}/状态`, { method: 'POST', body: JSON.stringify({ 状态: status }) })
      setMsg('地磅状态已更新')
      await load()
    } catch (e) { setErr(e.message) }
  }
  const create = async () => {
    setErr(''); setMsg('')
    try {
      await api('/地磅', { method: 'POST', body: JSON.stringify({ 回收点编号: Number(siteId), 地磅: code }) })
      setCode('')
      setMsg('地磅已新增')
      await load()
    } catch (e) { setErr(e.message) }
  }
  return (
    <div className="panel">
      <h2>地磅</h2>
      <div className="row">
        <label>回收点
          <select value={siteId} onChange={(e) => setSiteId(e.target.value)}>
            {sites.map((s) => <option key={s.编号} value={s.编号}>{s.名称}</option>)}
          </select>
        </label>
        <label>地磅号<input value={code} onChange={(e) => setCode(e.target.value)} /></label>
        <button type="button" onClick={create}>新增</button>
      </div>
      {msg && <div className="msg">{msg}</div>}
      {err && <div className="err">{err}</div>}
      <table>
        <thead><tr><th>回收点</th><th>地磅</th><th>状态</th><th>备注</th><th>操作</th></tr></thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.编号}>
              <td>{r.回收点}</td><td>{r.地磅}</td><td>{r.状态}</td><td>{r.备注 || '-'}</td>
              <td>
                {r.状态 === '空闲' && <button type="button" onClick={() => setStatus(r.编号, '故障')}>标故障</button>}
                {r.状态 === '故障' && <button type="button" className="secondary" onClick={() => setStatus(r.编号, '空闲')}>恢复空闲</button>}
                {r.状态 === '占用' && <span className="muted">过磅占用中</span>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
