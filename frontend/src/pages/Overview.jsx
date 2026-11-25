import React, { useEffect, useState } from 'react'
import { api } from '../api'

export default function Overview() {
  const [data, setData] = useState(null)
  const [err, setErr] = useState('')
  const load = () => api('/总览').then(setData).catch((e) => setErr(e.message))
  useEffect(() => { load() }, [])
  if (err) return <div className="panel err">{err}</div>
  if (!data) return <div className="panel">加载中</div>
  const d = data.分布 || {}
  const shift = data.班次
  return (
    <div className="panel">
      <h2>总览</h2>
      <p className="muted">
        当前班次：{shift ? `${shift.营业日} ${shift.班次名} · ${shift.状态}` : '无班次'}
      </p>
      <div className="grid">
        {Object.entries(d).map(([k, v]) => (
          <div className="stat" key={k}><div className="n">{v}</div><div className="l">{k}</div></div>
        ))}
      </div>
      <div className="table-wrap">
        <table>
          <thead><tr><th>回收点</th><th>地磅</th><th>状态</th><th>回收点状态</th></tr></thead>
          <tbody>
            {(data.地磅 || []).map((c) => (
              <tr key={c.编号}><td>{c.回收点}</td><td>{c.地磅}</td><td>{c.状态}</td><td>{c.回收点状态}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="row"><button type="button" className="secondary" onClick={load}>刷新</button></div>
    </div>
  )
}
