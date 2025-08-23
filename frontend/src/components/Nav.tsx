import React from 'react'
import { Link, useLocation } from 'react-router-dom'

function Tab({to, children}:{to:string, children:React.ReactNode}) {
  const loc = useLocation()
  const active = loc.pathname === to
  return (
    <Link to={to} className={"px-3 py-2 rounded-md text-sm " + (active ? "btn-neon" : "hover:btn-neon")}>
      {children}
    </Link>
  )
}

export default function Nav() {
  return (
    <nav className="flex items-center justify-between py-4">
      <h1 className="text-2xl neon-title drop-shadow-glow">OPΛ|OID • AI • DASHBOARD</h1>
      <div className="flex gap-3">
        <Tab to="/">Overview</Tab>
        <Tab to="/map">Map</Tab>
        <Tab to="/forecast">Forecast</Tab>
      </div>
    </nav>
  )
}
