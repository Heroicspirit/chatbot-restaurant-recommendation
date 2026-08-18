import React, { useEffect, useState } from 'react'
import MetricCard from './charts/MetricCard'
import DonutChart from './charts/DonutChart'
import BarChart from './charts/BarChart'
import TableView from './charts/TableView'
import { getRestaurants } from '../services/api'
import { IconUtensils, IconStar, IconSparkle, IconTag } from './icons'
import './Dashboard.css'

export default function Dashboard() {
  const [restaurants, setRestaurants] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getRestaurants()
      .then(data => {
        const list = Array.isArray(data) ? data : (data.restaurants || [])
        setRestaurants(list)
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner" />
        <p>Loading analytics...</p>
      </div>
    )
  }

  const total = restaurants.length
  const areas = [...new Set(restaurants.map(r => r.area).filter(Boolean))]
  const cuisines = [...new Set(
    restaurants.flatMap(r => r.cuisine?.split(',').map(c => c.trim()) || [])
  )]

  const avgRating = restaurants.reduce((s, r) => s + (parseFloat(r.rating) || 0), 0) / total
  const avgPrice = restaurants.reduce((s, r) => s + (parseFloat(r.avg_price_per_person) || 0), 0) / total

  const priceTiers = [
    { label: 'Budget-friendly', value: restaurants.filter(r => (r.price_level || '').toLowerCase() === 'low').length, color: 'var(--chart-2)' },
    { label: 'Moderate', value: restaurants.filter(r => (r.price_level || '').toLowerCase() === 'medium').length, color: 'var(--chart-1)' },
    { label: 'Premium', value: restaurants.filter(r => (r.price_level || '').toLowerCase() === 'high').length, color: 'var(--chart-5)' },
  ]

  const cuisineCounts = {}
  restaurants.forEach(r => {
    const list = (r.cuisine || '').split(',').map(c => c.trim()).filter(Boolean)
    list.forEach(c => { cuisineCounts[c] = (cuisineCounts[c] || 0) + 1 })
  })
  const cuisineData = Object.entries(cuisineCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(([label, value]) => ({ label, value }))

  const areaData = areas.map(area => ({
    label: area,
    value: restaurants.filter(r => r.area === area).length,
  })).sort((a, b) => b.value - a.value)

  const topRated = [...restaurants]
    .sort((a, b) => (parseFloat(b.rating) || 0) - (parseFloat(a.rating) || 0))
    .slice(0, 10)

  const dietaryOptions = ['veg', 'non-veg', 'both']
  const dietaryData = dietaryOptions.map(d => ({
    label: d.charAt(0).toUpperCase() + d.slice(1),
    value: restaurants.filter(r => (r.dietary || '').toLowerCase() === d || (d === 'both' && !r.dietary)).length,
    color: d === 'veg' ? 'var(--chart-2)' : d === 'non-veg' ? 'var(--chart-4)' : 'var(--chart-1)',
  }))

  const ratingRanges = [
    { label: '4.5+', value: restaurants.filter(r => parseFloat(r.rating) >= 4.5).length, color: 'var(--chart-2)' },
    { label: '4.0–4.4', value: restaurants.filter(r => { const rt = parseFloat(r.rating); return rt >= 4.0 && rt < 4.5 }).length, color: 'var(--chart-3)' },
    { label: '3.5–3.9', value: restaurants.filter(r => { const rt = parseFloat(r.rating); return rt >= 3.5 && rt < 4.0 }).length, color: 'var(--chart-1)' },
    { label: 'Below 3.5', value: restaurants.filter(r => { const rt = parseFloat(r.rating); return rt > 0 && rt < 3.5 }).length, color: 'var(--chart-4)' },
    { label: 'Unrated', value: restaurants.filter(r => !r.rating || parseFloat(r.rating) <= 0).length, color: 'var(--chart-5)' },
  ]

  const tableColumns = [
    { key: 'name', label: 'Restaurant', width: '30%' },
    { key: 'area', label: 'Area' },
    { key: 'cuisine', label: 'Cuisine' },
    {
      key: 'rating', label: 'Rating', width: '80px',
      render: (val) => val ? <span className="rating-star"><IconStar size={11} /> {val}</span> : '—',
    },
    {
      key: 'avg_price_per_person', label: 'Price', width: '100px',
      render: (val) => val ? `Rs. ${Number(val).toLocaleString()}` : '—',
    },
  ]

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>Restaurant Analytics</h2>
        <p className="dashboard-subtitle">Overview of the Kathmandu restaurant dataset</p>
      </div>

      <div className="dashboard-grid">
        <MetricCard
          label="Total Restaurants"
          value={total}
          subtitle={`Across ${areas.length} areas`}
          color="var(--chart-2)"
          icon={<IconUtensils size={16} />}
        />
        <MetricCard
          label="Average Rating"
          value={avgRating ? avgRating.toFixed(1) : '—'}
          subtitle="Out of 5.0"
          color="var(--chart-1)"
          icon={<IconStar size={16} />}
        />
        <MetricCard
          label="Cuisine Types"
          value={cuisines.length}
          subtitle="Unique cuisines available"
          color="var(--chart-3)"
          icon={<IconSparkle size={16} />}
        />
        <MetricCard
          label="Avg. Price per Person"
          value={avgPrice ? `Rs. ${Math.round(avgPrice).toLocaleString()}` : '—'}
          subtitle="Across all restaurants"
          color="var(--chart-4)"
          icon={<IconTag size={16} />}
        />

        <div className="dashboard-panel wide">
          <BarChart
            data={areaData}
            title="Restaurants per Area"
          />
        </div>

        <div className="dashboard-panel">
          <DonutChart
            data={cuisineData}
            title="Cuisine Distribution"
            size={140}
          />
        </div>

        <div className="dashboard-panel">
          <DonutChart
            data={dietaryData}
            title="Dietary Options"
            size={140}
          />
        </div>

        <div className="dashboard-panel">
          <BarChart
            data={ratingRanges}
            title="Rating Distribution"
          />
        </div>

        <div className="dashboard-panel">
          <DonutChart
            data={priceTiers}
            title="Price Tiers"
            size={140}
          />
        </div>

        <div className="dashboard-panel wide full">
          <TableView
            columns={tableColumns}
            data={topRated}
            title="Top Rated Restaurants"
            maxRows={8}
          />
        </div>
      </div>
    </div>
  )
}