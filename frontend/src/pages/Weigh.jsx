import React, { useEffect, useState } from 'react'
import { api } from '../api'

export default function Weigh() {
  const [sites, setSites] = useState([])
  const [scales, setScales] = useState([])
  const [rows, setRows] = useState([])
  const [siteId, setSiteId] = useState('')
  const [scaleId, setScaleId] = useState('')
  const [gross, setGross] = useState('1200')
  const [tare, setTare] = useState('800')
  const [deduct, setDeduct] = useState('0')
  const [msg, setMsg] = useState('')
  const [err, setErr] = useState('')

  const load = async () => {
    const [s, sc, open] = await Promise.all([api('/回收点'), api('/地磅'), api('/过磅')])
    setSites(s)
    setScales(sc)
    setRows(open)
    const openSites = s.filter((x) => x.状态 === '营业中')
    const sid = siteId || (openSites[0] && String(openSites[0].编号)) || ''
    if (!siteId && sid) setSiteId(sid)
    const free = sc.filter((x) => String(x.回收点编号) === String(sid || siteId) && x.状态 === '空闲' && x.回收点状态 === '营业中')
    const stillFree = free.some((x) => String(x.编号) === String(scaleId))
    if (!stillFree) setScaleId(free[0] ? String(free[0].编号) : '')
  }
  useEffect(() => { load().catch((e) => setErr(e.message)) }, [])

  const siteScales = scales.filter((x) => String(x.回收点编号) === String(siteId) && x.状态 === '空闲')

  const submit = async () => {
    setErr(''); setMsg('')
    try {
      const row = await api('/过磅', {
        method: 'POST',
        body: JSON.stringify({
          回收点编号: Number(siteId),
          地磅编号: Number(scaleId),
          毛重: Number(gross),
          皮重: Number(tare),
          扣杂: Number(deduct),
        }),
      })
      setMsg(`入站成功，磅条 ${row.磅条号}，地磅已占用`)
      setScaleId('')
      await load()
    } catch (e) { setErr(e.message) }
  }

  return (
    <div className="panel">
      <h2>过磅</h2>
      <div className="row">
        <label>回收点
          <select value={siteId} onChange={(e) => { setSiteId(e.target.value); setScaleId('') }}>
            {sites.filter((s) => s.状态 === '营业中').map((s) => (
              <option key={s.编号} value={s.编号}>{s.名称}</option>
            ))}
          </select>
        </label>
        <label>地磅
          <select value={scaleId} onChange={(e) => setScaleId(e.target.value)}>
            <option value="">请选择空闲地磅</option>
            {siteScales.map((s) => (
              <option key={s.编号} value={s.编号}>{s.地磅}</option>
            ))}
          </select>
        </label>
        <label>毛重<input value={gross} onChange={(e) => setGross(e.target.value)} /></label>
        <label>皮重<input value={tare} onChange={(e) => setTare(e.target.value)} /></label>
        <label>扣杂<input value={deduct} onChange={(e) => setDeduct(e.target.value)} /></label>
        <button type="button" onClick={submit} disabled={!scaleId}>入站占秤</button>
      </div>
      {msg && <div className="msg">{msg}</div>}
      {err && <div className="err">{err}</div>}
      <div className="table-wrap">
        <table>
          <thead><tr><th>磅条号</th><th>回收点</th><th>地磅</th><th>状态</th><th>毛重</th><th>皮重</th><th>扣杂</th><th>净重</th></tr></thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.编号}>
                <td>{r.磅条号}</td><td>{r.回收点}</td><td>{r.地磅}</td><td>{r.状态}</td>
                <td>{r.毛重}</td><td>{r.皮重}</td><td>{r.扣杂}</td><td>{r.净重}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
