import React, { useEffect, useState } from 'react'
import { api } from '../api'

export default function Grades() {
  const [rows, setRows] = useState([])
  const [cat, setCat] = useState('废纸')
  const [name, setName] = useState('')
  const [price, setPrice] = useState('1.00')
  const [err, setErr] = useState('')
  const [msg, setMsg] = useState('')
  const load = () => api('/品级').then(setRows).catch((e) => setErr(e.message))
  useEffect(() => { load() }, [])
  const save = async () => {
    setErr(''); setMsg('')
    try {
      await api('/品级', { method: 'POST', body: JSON.stringify({ 品类: cat, 品级名: name, 单价: Number(price) }) })
      setMsg('价目已保存')
      setName('')
      await load()
    } catch (e) { setErr(e.message) }
  }
  return (
    <div className="panel">
      <h2>品级</h2>
      <div className="row">
        <label>品类<input value={cat} onChange={(e) => setCat(e.target.value)} /></label>
        <label>品级名<input value={name} onChange={(e) => setName(e.target.value)} /></label>
        <label>单价<input value={price} onChange={(e) => setPrice(e.target.value)} /></label>
        <button type="button" onClick={save}>保存价目</button>
      </div>
      {msg && <div className="msg">{msg}</div>}
      {err && <div className="err">{err}</div>}
      <table>
        <thead><tr><th>品类</th><th>品级名</th><th>单价</th></tr></thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.编号}><td>{r.品类}</td><td>{r.品级名}</td><td>{r.单价}</td></tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
