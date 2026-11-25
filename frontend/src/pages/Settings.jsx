import React, { useEffect, useState } from 'react'
import { api } from '../api'

export default function Settings() {
  const [rows, setRows] = useState([])
  const [key, setKey] = useState('毛重软上限')
  const [val, setVal] = useState('40000')
  const [err, setErr] = useState('')
  const [msg, setMsg] = useState('')
  const load = () => api('/设置').then(setRows).catch((e) => setErr(e.message))
  useEffect(() => { load() }, [])
  const save = async () => {
    setErr(''); setMsg('')
    try {
      await api('/设置', { method: 'POST', body: JSON.stringify({ 键: key, 值: val }) })
      setMsg('已保存')
      await load()
    } catch (e) { setErr(e.message) }
  }
  return (
    <div className="panel">
      <h2>设置</h2>
      {msg && <div className="msg">{msg}</div>}
      {err && <div className="err">{err}</div>}
      <div className="row">
        <label>键<input value={key} onChange={(e) => setKey(e.target.value)} /></label>
        <label>值<input value={val} onChange={(e) => setVal(e.target.value)} /></label>
        <button type="button" onClick={save}>保存</button>
      </div>
      <table>
        <thead><tr><th>键</th><th>值</th></tr></thead>
        <tbody>{rows.map((r) => <tr key={r.键}><td>{r.键}</td><td>{r.值}</td></tr>)}</tbody>
      </table>
    </div>
  )
}
