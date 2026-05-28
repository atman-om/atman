'use client';

import { useCallback, useEffect, useState } from 'react';
import type React from 'react';
import { API_BASE } from '../lib/api';

type AuthState = {
  token: string;
  role: 'admin' | 'operator';
};

type FetchState<T> = {
  data: T | null;
  error: string | null;
  loading: boolean;
};

const AUTH_KEY = 'atman.console.auth';

function readAuth(): AuthState {
  if (typeof window === 'undefined') return { token: '', role: 'admin' };
  try {
    const parsed = JSON.parse(window.localStorage.getItem(AUTH_KEY) || '{}') as Partial<AuthState>;
    return { token: parsed.token || '', role: parsed.role === 'operator' ? 'operator' : 'admin' };
  } catch {
    return { token: '', role: 'admin' };
  }
}

function authHeaders(auth: AuthState): HeadersInit {
  const headers: Record<string, string> = { 'X-Atman-Role': auth.role };
  if (auth.token.trim()) headers.Authorization = `Bearer ${auth.token.trim()}`;
  return headers;
}

async function apiJson<T>(path: string, auth: AuthState, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    cache: 'no-store',
    ...init,
    headers: {
      ...authHeaders(auth),
      ...(init?.body ? { 'Content-Type': 'application/json' } : {}),
      ...(init?.headers || {}),
    },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `${res.status} ${res.statusText}`);
  }
  return (await res.json()) as T;
}

function useAuth() {
  const [auth, setAuth] = useState<AuthState>({ token: '', role: 'admin' });
  useEffect(() => setAuth(readAuth()), []);
  const save = useCallback((next: AuthState) => {
    setAuth(next);
    window.localStorage.setItem(AUTH_KEY, JSON.stringify(next));
  }, []);
  const clear = useCallback(() => save({ token: '', role: 'admin' }), [save]);
  return { auth, save, clear };
}

function useApi<T>(path: string, auth: AuthState): FetchState<T> & { reload: () => void } {
  const [state, setState] = useState<FetchState<T>>({ data: null, error: null, loading: true });
  const [reloadKey, setReloadKey] = useState(0);
  const reload = useCallback(() => setReloadKey((value) => value + 1), []);
  useEffect(() => {
    let alive = true;
    setState((current) => ({ ...current, loading: true, error: null }));
    apiJson<T>(path, auth)
      .then((data) => alive && setState({ data, error: null, loading: false }))
      .catch((error: Error) => alive && setState({ data: null, error: error.message, loading: false }));
    return () => {
      alive = false;
    };
  }, [path, auth.token, auth.role, reloadKey]);
  return { ...state, reload };
}

function AuthPanel({ auth, onSave, onClear }: { auth: AuthState; onSave: (next: AuthState) => void; onClear: () => void }) {
  const [token, setToken] = useState(auth.token);
  const [role, setRole] = useState<AuthState['role']>(auth.role);
  useEffect(() => {
    setToken(auth.token);
    setRole(auth.role);
  }, [auth.token, auth.role]);
  return (
    <section className="auth-panel">
      <div>
        <span className="eyebrow">Access</span>
        <h2>Console Login</h2>
        <p>Use the admin token when production auth is enabled. Local development can stay empty.</p>
      </div>
      <div className="auth-form">
        <select value={role} onChange={(event) => setRole(event.target.value as AuthState['role'])}>
          <option value="admin">Admin</option>
          <option value="operator">Operator</option>
        </select>
        <input value={token} onChange={(event) => setToken(event.target.value)} placeholder="Admin bearer token" type="password" />
        <button onClick={() => onSave({ token, role })}>Save access</button>
        {auth.token ? <button className="secondary" onClick={onClear}>Clear</button> : null}
      </div>
    </section>
  );
}

export function ConsoleShell({ children }: { children: (auth: AuthState) => React.ReactNode }) {
  const { auth, save, clear } = useAuth();
  return (
    <>
      <AuthPanel auth={auth} onSave={save} onClear={clear} />
      {children(auth)}
    </>
  );
}

export function Kpi({ label, value, detail, tone = 'neutral' }: { label: string; value: React.ReactNode; detail?: string; tone?: 'neutral' | 'good' | 'warn' | 'bad' }) {
  return (
    <div className={`kpi ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
      {detail ? <small>{detail}</small> : null}
    </div>
  );
}

export function Panel({ title, children, action }: { title: string; children: React.ReactNode; action?: React.ReactNode }) {
  return (
    <section className="card panel">
      <div className="panel-head">
        <h2>{title}</h2>
        {action}
      </div>
      {children}
    </section>
  );
}

export function StatusList({ items }: { items: Array<{ label: string; value: React.ReactNode; tone?: 'good' | 'warn' | 'bad' | 'neutral' }> }) {
  return (
    <div className="status-list">
      {items.map((item) => <div key={item.label}><span>{item.label}</span><b className={item.tone || 'neutral'}>{item.value}</b></div>)}
    </div>
  );
}

export function ErrorBox({ message }: { message: string | null }) {
  if (!message) return null;
  return <div className="error-box">{message}</div>;
}

function Loading({ label = 'Loading' }: { label?: string }) {
  return <p className="empty-state">{label}...</p>;
}

type DashboardPayload = {
  os: any;
  modelLab: any;
  analytics: any;
  readiness: any;
};

export function DashboardClient() {
  const { auth, save, clear } = useAuth();
  const os = useApi<any>('/os/status', auth);
  const modelLab = useApi<any>('/model-lab/readiness', auth);
  const analytics = useApi<any>('/analytics/overview', auth);
  const readiness = useApi<any>('/analytics/readiness', auth);
  const data: DashboardPayload = { os: os.data, modelLab: modelLab.data, analytics: analytics.data, readiness: readiness.data };
  const loading = os.loading || modelLab.loading || analytics.loading || readiness.loading;
  const errors = [os.error, modelLab.error, analytics.error, readiness.error].filter(Boolean).join('\n');
  return (
    <>
      <AuthPanel auth={auth} onSave={save} onClear={clear} />
      <section className="hero">
        <span className="badge">Atman v2.0</span>
        <h1>Dharma Knowledge OS</h1>
        <p>Live product console for Qwen serving, canonical corpus, learning, content, analytics, and production readiness.</p>
      </section>
      <ErrorBox message={errors || null} />
      {loading ? <Loading label="Loading console" /> : (
        <>
          <section className="kpi-grid">
            <Kpi label="Product" value={data.readiness?.ready_for_public_beta ? 'Beta ready' : 'Not beta ready'} tone={data.readiness?.ready_for_public_beta ? 'good' : 'warn'} detail={`v${data.readiness?.version || data.os?.version || 'unknown'}`} />
            <Kpi label="Model Lab" value={`${Math.round((data.modelLab?.readiness_score || 0) * 100)}%`} tone={(data.modelLab?.readiness_score || 0) > 0.7 ? 'good' : 'warn'} detail={data.modelLab?.fine_tuning_lane || 'parallel lane'} />
            <Kpi label="Canonical Passages" value={data.modelLab?.counts?.canonical_passages ?? data.analytics?.corpus?.canonical_passages ?? 0} detail="verified training signal" />
            <Kpi label="Chat Sessions" value={data.analytics?.chats?.sessions ?? 0} detail={`${data.analytics?.chats?.messages ?? 0} messages`} />
          </section>
          <section className="grid">
            <Panel title="Launch Surface">
              <div className="chip-row">{(data.os?.launch_surfaces || []).map((item: string) => <span className="chip" key={item}>{item}</span>)}</div>
            </Panel>
            <Panel title="Readiness">
              <StatusList items={[
                { label: 'Remote Qwen', value: data.readiness?.checks?.remote_qwen_mode || data.os?.primary_runtime || 'unknown', tone: data.readiness?.blockers?.length ? 'warn' : 'good' },
                { label: 'Users', value: data.readiness?.checks?.users ?? 0 },
                { label: 'Canonical Works', value: data.readiness?.checks?.canonical_works ?? 0 },
                { label: 'Blockers', value: data.readiness?.blockers?.length ?? 0, tone: data.readiness?.blockers?.length ? 'bad' : 'good' },
              ]} />
            </Panel>
            <Panel title="Next Actions">
              <ul className="plain-list">{(data.modelLab?.next_actions || data.readiness?.warnings || []).slice(0, 5).map((item: string) => <li key={item}>{item}</li>)}</ul>
            </Panel>
          </section>
        </>
      )}
    </>
  );
}

export function QwenClient() {
  return (
    <ConsoleShell>{(auth) => <QwenContent auth={auth} />}</ConsoleShell>
  );
}

function QwenContent({ auth }: { auth: AuthState }) {
  const status = useApi<any>('/qwen/serving/status', auth);
  const profiles = useApi<any[]>('/qwen/serving/profiles', auth);
  return (
    <>
      <ErrorBox message={status.error || profiles.error} />
      {status.loading || profiles.loading ? <Loading label="Loading Qwen gateway" /> : (
        <section className="grid">
          <Panel title="Serving Status">
            <StatusList items={[
              { label: 'Runtime', value: status.data?.serving?.runtime_mode || 'unknown' },
              { label: 'Model', value: status.data?.serving?.model_id || 'unknown' },
              { label: 'Remote health', value: status.data?.remote_health?.reachable ? 'Reachable' : 'Not configured', tone: status.data?.remote_health?.reachable ? 'good' : 'warn' },
              { label: 'Weights bundled', value: status.data?.weights_bundled ? 'Yes' : 'No' },
            ]} />
            <p className="muted">{status.data?.message}</p>
          </Panel>
          <Panel title="Serving Profiles">
            <div className="table-list">{(profiles.data || []).map((profile) => (
              <div key={profile.name}>
                <b>{profile.name}</b>
                <span>{profile.mode}</span>
                <small>{profile.endpoint || profile.command}</small>
              </div>
            ))}</div>
          </Panel>
        </section>
      )}
    </>
  );
}

export function AccountsClient() {
  return <ConsoleShell>{(auth) => <AccountsContent auth={auth} />}</ConsoleShell>;
}

function AccountsContent({ auth }: { auth: AuthState }) {
  const me = useApi<any>('/accounts/me', auth);
  const users = useApi<any[]>('/accounts/users', auth);
  return (
    <>
      <ErrorBox message={me.error || users.error} />
      {me.loading || users.loading ? <Loading label="Loading accounts" /> : (
        <section className="grid">
          <Panel title="Current User">
            <StatusList items={[
              { label: 'Name', value: me.data?.display_name || 'unknown' },
              { label: 'Email', value: me.data?.email || 'unknown' },
              { label: 'Role', value: me.data?.role || 'unknown' },
            ]} />
          </Panel>
          <Panel title="Users">
            <div className="table-list">{(users.data || []).map((user) => (
              <div key={user.id}>
                <b>{user.display_name || user.email}</b>
                <span>{user.role}</span>
                <small>{user.email}</small>
              </div>
            ))}</div>
          </Panel>
        </section>
      )}
    </>
  );
}

export function AnalyticsClient() {
  return <ConsoleShell>{(auth) => <AnalyticsContent auth={auth} />}</ConsoleShell>;
}

function AnalyticsContent({ auth }: { auth: AuthState }) {
  const overview = useApi<any>('/analytics/overview', auth);
  const readiness = useApi<any>('/analytics/readiness', auth);
  return (
    <>
      <ErrorBox message={overview.error || readiness.error} />
      {overview.loading || readiness.loading ? <Loading label="Loading analytics" /> : (
        <section className="grid">
          <Panel title="Overview">
            <div className="kpi-grid">
              <Kpi label="Chats" value={overview.data?.chats?.sessions ?? 0} detail={`${overview.data?.chats?.messages ?? 0} messages`} />
              <Kpi label="Canonical" value={overview.data?.corpus?.canonical_passages ?? 0} detail="passages" />
              <Kpi label="Cost" value={overview.data?.billing?.estimated_model_cost ?? 0} detail={overview.data?.billing?.currency || 'USD'} />
            </div>
          </Panel>
          <Panel title="Readiness">
            <StatusList items={[
              { label: 'Demo', value: readiness.data?.ready_for_demo ? 'Ready' : 'Blocked', tone: readiness.data?.ready_for_demo ? 'good' : 'warn' },
              { label: 'Public beta', value: readiness.data?.ready_for_public_beta ? 'Ready' : 'Blocked', tone: readiness.data?.ready_for_public_beta ? 'good' : 'warn' },
              { label: 'Blockers', value: readiness.data?.blockers?.length ?? 0, tone: readiness.data?.blockers?.length ? 'bad' : 'good' },
            ]} />
          </Panel>
        </section>
      )}
    </>
  );
}

export function ModelLabClient() {
  return <ConsoleShell>{(auth) => <ModelLabContent auth={auth} />}</ConsoleShell>;
}

function ModelLabContent({ auth }: { auth: AuthState }) {
  const readiness = useApi<any>('/model-lab/readiness', auth);
  const comparison = useApi<any>('/model-lab/comparison', auth);
  const experiments = useApi<any[]>('/model-lab/experiments', auth);
  return (
    <>
      <ErrorBox message={readiness.error || comparison.error || experiments.error} />
      {readiness.loading || comparison.loading || experiments.loading ? <Loading label="Loading model lab" /> : (
        <section className="grid">
          <Panel title="Readiness">
            <div className="kpi-grid">
              <Kpi label="Score" value={`${Math.round((readiness.data?.readiness_score || 0) * 100)}%`} />
              <Kpi label="Passages" value={readiness.data?.counts?.canonical_passages ?? 0} />
              <Kpi label="Failure cases" value={readiness.data?.counts?.failure_cases ?? 0} />
            </div>
            <StatusList items={[
              { label: 'Mode', value: readiness.data?.mode || 'unknown' },
              { label: 'Production replacement', value: readiness.data?.production_replacement_allowed ? 'Allowed' : 'Blocked', tone: readiness.data?.production_replacement_allowed ? 'good' : 'warn' },
            ]} />
          </Panel>
          <Panel title="Comparison"><Summary data={comparison.data} /></Panel>
          <Panel title="Experiments"><Summary data={experiments.data} /></Panel>
        </section>
      )}
    </>
  );
}

export function ResourceClient({ title, endpoints }: { title: string; endpoints: Array<{ title: string; path: string; summarize?: (data: any) => React.ReactNode }> }) {
  return <ConsoleShell>{(auth) => <ResourceContent auth={auth} title={title} endpoints={endpoints} />}</ConsoleShell>;
}

function ResourceContent({ auth, title, endpoints }: { auth: AuthState; title: string; endpoints: Array<{ title: string; path: string; summarize?: (data: any) => React.ReactNode }> }) {
  return (
    <>
      <section className="hero compact-hero">
        <h1>{title}</h1>
      </section>
      <section className="grid">
        {endpoints.map((endpoint) => <EndpointPanel key={endpoint.path} auth={auth} endpoint={endpoint} />)}
      </section>
    </>
  );
}

function EndpointPanel({ auth, endpoint }: { auth: AuthState; endpoint: { title: string; path: string; summarize?: (data: any) => React.ReactNode } }) {
  const result = useApi<any>(endpoint.path, auth);
  return (
    <Panel title={endpoint.title}>
      <ErrorBox message={result.error} />
      {result.loading ? <Loading /> : endpoint.summarize ? endpoint.summarize(result.data) : <Summary data={result.data} />}
    </Panel>
  );
}

function Summary({ data }: { data: any }) {
  if (Array.isArray(data)) {
    if (!data.length) return <p className="empty-state">No records yet.</p>;
    return <div className="table-list">{data.slice(0, 12).map((item, index) => <div key={item?.id || index}><b>{item?.title_hi || item?.title_en || item?.name || item?.work_key || item?.id || `Record ${index + 1}`}</b><span>{item?.status || item?.role || item?.category || item?.review_status || 'record'}</span></div>)}</div>;
  }
  if (!data) return <p className="empty-state">No data.</p>;
  const pairs = Object.entries(data).filter(([, value]) => typeof value !== 'object').slice(0, 8);
  return <StatusList items={pairs.map(([label, value]) => ({ label, value: String(value) }))} />;
}

export function CanonicalClient() {
  return <ConsoleShell>{(auth) => <CanonicalContent auth={auth} />}</ConsoleShell>;
}

function CanonicalContent({ auth }: { auth: AuthState }) {
  const works = useApi<any[]>('/canonical/works', auth);
  const [seedMessage, setSeedMessage] = useState<string | null>(null);
  const seed = async () => {
    setSeedMessage('Seeding canonical corpus...');
    try {
      const response = await apiJson<any>('/canonical/seed/demo', auth, { method: 'POST' });
      setSeedMessage(`Seed ready: ${response.imported.works} works, ${response.imported.passages} passages`);
      works.reload();
    } catch (error) {
      setSeedMessage(error instanceof Error ? error.message : 'Seed failed');
    }
  };
  return (
    <>
      <ErrorBox message={works.error} />
      <section className="grid">
        <Panel title="Canonical Works" action={<button onClick={seed}>Seed demo corpus</button>}>
          {seedMessage ? <p className="muted">{seedMessage}</p> : null}
          {works.loading ? <Loading /> : (
            <div className="table-list">{(works.data || []).map((work) => (
              <div key={work.id}>
                <b>{work.title_hi || work.title_en || work.work_key}</b>
                <span>{work.category}</span>
                <small>{work.canonical_status} - {work.authority_level}</small>
              </div>
            ))}</div>
          )}
        </Panel>
        <Panel title="Corpus Health">
          <Kpi label="Works" value={works.data?.length || 0} detail="canonical entries" />
          <p className="muted">Use the seed action for local/demo data. Production imports should still come from reviewed manifests.</p>
        </Panel>
      </section>
    </>
  );
}
