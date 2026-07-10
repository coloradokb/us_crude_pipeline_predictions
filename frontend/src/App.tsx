import { type ReactNode, useEffect, useMemo, useState } from "react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Activity, AlertCircle, Database, RefreshCw } from "lucide-react";

import { fetchPredictions } from "./api";
import type { PredictionRow } from "./types";

const SERIES = "WCESTUS1";

type LoadState = "idle" | "loading" | "ready" | "error";

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "2-digit",
  }).format(new Date(`${value}T00:00:00`));
}

function formatWhole(value: number | null | undefined): string {
  if (value === null || value === undefined) return "Pending";
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(value);
}

function formatPercent(value: number | null): string {
  if (value === null) return "-";
  return `${(value * 100).toFixed(2)}%`;
}

function App() {
  const [predictions, setPredictions] = useState<PredictionRow[]>([]);
  const [loadState, setLoadState] = useState<LoadState>("idle");
  const [error, setError] = useState<string | null>(null);

  async function loadPredictions() {
    setLoadState("loading");
    setError(null);
    try {
      const data = await fetchPredictions(SERIES);
      setPredictions(data);
      setLoadState("ready");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown API error");
      setLoadState("error");
    }
  }

  useEffect(() => {
    void loadPredictions();
  }, []);

  const latest = predictions[predictions.length - 1];
  const historicalRows = predictions.filter((row) => row.actual !== null);

  const chartData = predictions.map((row) => ({
    date: formatDate(row.target_period),
    targetPeriod: row.target_period,
    prediction: row.prediction,
    actual: row.actual,
    errorRate: row.error_rate ? row.error_rate * 100 : null,
  }));
  const tableRows = [...predictions].sort((left, right) =>
    right.target_period.localeCompare(left.target_period),
  );
  const inventoryDomain = useMemo((): [number, number] => {
    const values = chartData.flatMap((row) => [
      row.prediction,
      ...(row.actual === null ? [] : [row.actual]),
    ]);
    if (values.length === 0) return [0, 100000];

    const min = Math.min(...values);
    const max = Math.max(...values);
    const rawSpan = max - min;
    const span = Math.min(Math.max(rawSpan * 1.35, 20000), 100000);
    const midpoint = (min + max) / 2;
    const lower = Math.max(0, Math.floor((midpoint - span / 2) / 5000) * 5000);
    const upper = Math.ceil((midpoint + span / 2) / 5000) * 5000;
    return [lower, upper];
  }, [chartData]);

  return (
    <>
      <header className="site-header">
        <a className="brand" href="https://www.coloradokb.com/" aria-label="ColoradoKB home">
          <span className="brand-mark">KB</span>
          <span>ColoradoKB</span>
        </a>
        <nav className="site-nav" aria-label="Primary navigation">
          <a href="https://www.coloradokb.com/">Home</a>
          <a href="https://ml.coloradokb.com/">Projects</a>
          <a href="https://github.com/coloradokb">GitHub</a>
        </nav>
      </header>

      <main>
        <section className="dashboard-hero" aria-labelledby="dashboard-title">
          <div className="hero-copy">
            <p className="eyebrow">EIA weekly crude inventory forecast</p>
            <h1 id="dashboard-title">WCESTUS1</h1>
            <p className="hero-text">
              One-week inventory predictions for U.S. ending stocks excluding SPR, with
              historical backfill rows for prediction-vs-actual comparison.
            </p>
          </div>

          <div className="summary-grid two-up" aria-label="Prediction summary">
            <MetricCard
              icon={<Activity aria-hidden="true" />}
              label="Latest prediction"
              value={formatWhole(latest?.prediction)}
              detail={latest ? `Target ${latest.target_period}` : "Waiting for API data"}
            />
            <MetricCard
              icon={<Database aria-hidden="true" />}
              label="Last EIA Data"
              value={latest?.source_data_through_period ?? "-"}
              detail={latest ? "Latest observed report week" : "Waiting for API data"}
            />
          </div>
        </section>

        <section className="toolbar" aria-label="Dashboard controls">
          <div>
            <span className={`status-dot ${loadState}`} aria-hidden="true" />
            <span>{loadState === "ready" ? "Connected" : loadState}</span>
          </div>
          <button className="icon-button" type="button" onClick={() => void loadPredictions()}>
            <RefreshCw size={18} aria-hidden="true" />
            Refresh
          </button>
        </section>

        {error ? (
          <section className="notice" role="alert">
            <AlertCircle aria-hidden="true" />
            <span>{error}</span>
          </section>
        ) : null}

        <section className="panel-grid">
          <article className="panel chart-panel">
            <div className="panel-heading">
              <div>
                <p className="panel-kicker">Forecast line</p>
                <h2>Prediction vs actual</h2>
              </div>
            </div>
            <div className="chart-wrap">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 10, right: 18, left: 0, bottom: 0 }}>
                  <CartesianGrid stroke="#d8e3e8" vertical={false} />
                  <XAxis dataKey="date" tickLine={false} axisLine={false} />
                  <YAxis
                    width={70}
                    domain={inventoryDomain}
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(value) => `${Math.round(Number(value) / 1000)}k`}
                  />
                  <Tooltip
                    formatter={(value) => formatWhole(Number(value))}
                    labelFormatter={(_, payload) => payload?.[0]?.payload?.targetPeriod ?? ""}
                  />
                  <Line
                    type="monotone"
                    dataKey="prediction"
                    name="Prediction"
                    stroke="#0b6f91"
                    strokeWidth={3}
                    dot={{ r: 3 }}
                    activeDot={{ r: 5 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="actual"
                    name="Actual"
                    stroke="#c97918"
                    strokeWidth={3}
                    dot={{ r: 3 }}
                    activeDot={{ r: 5 }}
                    connectNulls={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </article>

          <article className="panel chart-panel">
            <div className="panel-heading">
              <div>
                <p className="panel-kicker">Error rate</p>
                <h2>Backfill miss percentage</h2>
              </div>
            </div>
            <div className="chart-wrap">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData} margin={{ top: 10, right: 18, left: 0, bottom: 0 }}>
                  <CartesianGrid stroke="#d8e3e8" vertical={false} />
                  <XAxis dataKey="date" tickLine={false} axisLine={false} />
                  <YAxis
                    width={58}
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(value) => `${Number(value).toFixed(1)}%`}
                  />
                  <Tooltip
                    formatter={(value) => `${Number(value).toFixed(2)}%`}
                    labelFormatter={(_, payload) => payload?.[0]?.payload?.targetPeriod ?? ""}
                  />
                  <Area
                    type="monotone"
                    dataKey="errorRate"
                    name="Error"
                    stroke="#082f45"
                    fill="#4bb7df"
                    fillOpacity={0.22}
                    connectNulls={false}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </article>
        </section>

        <section className="data-panel" aria-label="Prediction data table">
          <div className="panel-heading">
            <div>
              <p className="panel-kicker">Rows for graphing</p>
              <h2>Prediction history</h2>
            </div>
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Target</th>
                  <th>Prediction</th>
                  <th>Actual</th>
                  <th>Error</th>
                  <th>Error %</th>
                  <th>Source through</th>
                </tr>
              </thead>
              <tbody>
                {tableRows.map((row) => (
                  <tr key={row.target_period}>
                    <td>{row.target_period}</td>
                    <td>{formatWhole(row.prediction)}</td>
                    <td>{formatWhole(row.actual)}</td>
                    <td className={row.value_error && row.value_error < 0 ? "negative" : ""}>
                      {formatWhole(row.value_error)}
                    </td>
                    <td className={row.error_rate && row.error_rate < 0 ? "negative" : ""}>
                      {formatPercent(row.error_rate)}
                    </td>
                    <td>{row.source_data_through_period}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </main>

      <footer className="site-footer">
        <span>ColoradoKB</span>
        <span>WCESTUS1 forecast dashboard</span>
      </footer>
    </>
  );
}

function MetricCard({
  icon,
  label,
  value,
  detail,
}: {
  icon: ReactNode;
  label: string;
  value: string;
  detail: string;
}) {
  return (
    <article className="metric-card">
      <div className="metric-icon">{icon}</div>
      <div>
        <p>{label}</p>
        <strong>{value}</strong>
        <span>{detail}</span>
      </div>
    </article>
  );
}

export default App;
