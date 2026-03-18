import { useState } from "react";
import {
  Shield, AlertTriangle, CheckCircle, Info, Lock, Globe, Server,
  Activity, ChevronDown, ChevronUp, Clock, Brain
} from "lucide-react";
import type {
  AnalyzeResponse, InfrastructureFeatures, DomainInfo
} from "@/types/analysis";
import { Button } from "@/components/ui/button";

/* ════════════════════════════════════════════════════════════════════════════
   Helpers
   ════════════════════════════════════════════════════════════════════════════ */

function riskColor(risk: string) {
  switch (risk) {
    case "HIGH":   return { text: "text-red-400",    border: "border-red-500/50", bg: "bg-red-500/5",    glow: "from-red-500/30 to-red-500/10",    dot: "bg-red-500 shadow-red-500/60" };
    case "MEDIUM": return { text: "text-orange-400",  border: "border-orange-500/50", bg: "bg-orange-500/5", glow: "from-orange-500/30 to-orange-500/10", dot: "bg-orange-500 shadow-orange-500/60" };
    case "LOW":    return { text: "text-yellow-400",  border: "border-yellow-500/50", bg: "bg-yellow-500/5", glow: "from-yellow-500/30 to-yellow-500/10", dot: "bg-yellow-500 shadow-yellow-500/60" };
    default:       return { text: "text-slate-400",   border: "border-slate-500/50", bg: "bg-slate-500/5",  glow: "from-slate-500/30 to-slate-500/10",  dot: "bg-slate-500 shadow-slate-500/60" };
  }
}

function signalDot(value: number | null | undefined, goodWhen: "positive" | "truthy" | "present" = "truthy") {
  if (value === null || value === undefined || value === -1) return "bg-slate-500";
  if (goodWhen === "truthy")   return value >= 1 ? "bg-emerald-500 shadow-emerald-500/60" : value === 0 ? "bg-red-500 shadow-red-500/60" : "bg-yellow-500 shadow-yellow-500/60";
  if (goodWhen === "positive") return value > 1 ? "bg-emerald-500 shadow-emerald-500/60" : value === 1 ? "bg-yellow-500 shadow-yellow-500/60" : "bg-red-500 shadow-red-500/60";
  return value === 1 ? "bg-emerald-500 shadow-emerald-500/60" : "bg-yellow-500 shadow-yellow-500/60";
}

/* ════════════════════════════════════════════════════════════════════════════
   Main Component
   ════════════════════════════════════════════════════════════════════════════ */

interface Props {
  result: AnalyzeResponse;
  onReset: () => void;
}

const AnalysisResults = ({ result, onReset }: Props) => {
  const isInvalid  = result.prediction === "invalid";
  const isPhishing = result.label === 1 && !isInvalid;
  const isSafe     = !isPhishing && !isInvalid;
  const risk       = result.risk_level;
  const colors     = isPhishing ? riskColor(risk) : isSafe
    ? { text: "text-emerald-400", border: "border-emerald-500/50", bg: "bg-emerald-500/5", glow: "from-emerald-500/30 to-emerald-500/10", dot: "bg-emerald-500 shadow-emerald-500/60" }
    : riskColor("HIGH");

  return (
    <div className="space-y-5 animate-slide-up">
      {/* Degraded Warning */}
      {result.degraded && !isInvalid && <DegradedBanner />}

      {/* 1 ▸ Verdict Card */}
      <VerdictCard isInvalid={isInvalid} isPhishing={isPhishing} risk={risk} colors={colors} reason={result.reason} />

      {/* 2 ▸ Prediction Details */}
      <PredictionDetails result={result} isInvalid={isInvalid} isPhishing={isPhishing} risk={risk} />

      {/* 3 ▸ Risk Explanation */}
      <RiskExplanation result={result} isInvalid={isInvalid} isPhishing={isPhishing} risk={risk} />


      {/* 5 ▸ Infrastructure Signals */}
      {result.infrastructure && <InfrastructureCard infra={result.infrastructure} />}

      {/* 6 ▸ Domain Intelligence */}
      <DomainIntelligenceCard domainInfo={result.domain_info} />



      {/* Reset */}
      <div className="flex justify-center pt-2">
        <Button
          onClick={onReset}
          variant="outline"
          className={`${colors.border} ${colors.text} hover:${colors.bg} hover:scale-105 transition-all duration-300 tracking-wide`}
        >
          CHECK ANOTHER URL
        </Button>
      </div>
    </div>
  );
};

/* ════════════════════════════════════════════════════════════════════════════
   Sub-Components
   ════════════════════════════════════════════════════════════════════════════ */

/* ── Degraded Banner ────────────────────────────────────────────────────── */
const DegradedBanner = () => (
  <div className="flex items-start gap-3 p-4 rounded-xl border border-yellow-600/50 bg-yellow-500/5 text-yellow-300 text-sm">
    <AlertTriangle className="w-5 h-5 shrink-0 mt-0.5" />
    <span><strong>Degraded Mode</strong> — Some infrastructure signals are unavailable. Prediction may be conservative and based on lexical features only.</span>
  </div>
);

/* ── Verdict Card ───────────────────────────────────────────────────────── */
const VerdictCard = ({ isInvalid, isPhishing, risk, colors, reason }: {
  isInvalid: boolean; isPhishing: boolean; risk: string;
  colors: ReturnType<typeof riskColor>; reason?: string | null;
}) => {
  let icon: React.ReactNode, title: string, sub: string;

  if (isInvalid) {
    icon  = <AlertTriangle className="w-10 h-10 text-red-400" />;
    title = "INVALID URL — HIGH RISK";
    sub   = reason || "Domain did not resolve (NXDOMAIN)";
  } else if (!isPhishing) {
    icon  = <CheckCircle className="w-10 h-10 text-emerald-400" />;
    title = "SAFE";
    sub   = "No threat detected";
  } else {
    icon  = risk === "HIGH"
      ? <AlertTriangle className="w-10 h-10 text-red-400" />
      : <AlertTriangle className={`w-10 h-10 ${risk === "MEDIUM" ? "text-orange-400" : "text-yellow-400"}`} />;
    title = `PHISHING — ${risk} RISK`;
    sub   = "Phishing probability detected";
  }

  return (
    <div className="relative group">
      <div className={`absolute -inset-0.5 bg-gradient-to-r ${colors.glow} rounded-2xl blur opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />
      <div className={`relative cyber-card border-2 ${colors.border} ${colors.bg} p-6 md:p-8 backdrop-blur-sm transition-all duration-300`}>
        <div className="flex items-center gap-5">
          <div className="relative shrink-0">
            <div className={`w-16 h-16 rounded-full flex items-center justify-center ${colors.bg} border-2 ${colors.border}`}>
              {icon}
            </div>
            <div className={`absolute inset-0 ${isPhishing ? "bg-red-500/20" : isInvalid ? "bg-red-500/20" : "bg-emerald-500/20"} blur-xl opacity-50 ${isPhishing || isInvalid ? "" : "animate-pulse"}`} />
          </div>
          <div>
            <h3 className={`text-xl md:text-2xl font-bold ${colors.text} tracking-tight`}>{title}</h3>
            <p className="text-muted-foreground mt-1">{sub}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

/* ── Prediction Details ─────────────────────────────────────────────────── */
const PredictionDetails = ({ result, isInvalid, isPhishing, risk }: {
  result: AnalyzeResponse; isInvalid: boolean; isPhishing: boolean; risk: string;
}) => {
  const items = [
    { label: "Verdict",    value: isInvalid ? "⚠ Invalid" : isPhishing ? "⚠ Phishing" : "✓ Safe" },
    { label: "Risk Level", value: risk },
    { label: "Model",      value: isInvalid ? "DNS Guard Pre-Check" : `Ensemble ${result.model_version}` },
    { label: "Latency",    value: `${Math.round(result.latency_ms)} ms` },
  ];

  return (
    <Card title="Prediction Details" icon={<Activity className="w-4 h-4" />}>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {items.map(i => (
          <div key={i.label} className="bg-background/50 rounded-xl p-3 border border-border/50">
            <div className="text-[0.68rem] text-muted-foreground uppercase tracking-wider">{i.label}</div>
            <div className="text-sm font-semibold mt-1 text-foreground">{i.value}</div>
          </div>
        ))}
      </div>
    </Card>
  );
};

function isSafe(r: AnalyzeResponse) { return r.label !== 1 && r.prediction !== "invalid"; }

/* ── Risk Explanation ───────────────────────────────────────────────────── */
const RiskExplanation = ({ result, isInvalid, isPhishing, risk }: {
  result: AnalyzeResponse; isInvalid: boolean; isPhishing: boolean; risk: string;
}) => {
  const di = result.domain_info;
  const infra = result.infrastructure;
  let text: React.ReactNode;

  if (isInvalid) {
    text = (
      <>
        🚨 <strong>Deterministic Failure:</strong> {result.reason || "Domain does not resolve (NXDOMAIN)"}.
        The DNS guard explicitly blocked this request before ML inference because the domain is unregistered or entirely dead.
        Real businesses maintain active DNS records.
      </>
    );
  } else if (!isPhishing) {
    text = (
      <>
        This URL appears <strong>safe</strong>
        {di?.whois_available && di?.domain_age && <> — the domain is <strong>{di.domain_age}</strong> old</>}
        {infra?.tls_ssl_certificate === 1 && <>, with a <strong>valid SSL/TLS certificate</strong></>}
        {infra?.qty_nameservers != null && infra.qty_nameservers > 1 && <> and <strong>{infra.qty_nameservers} name servers</strong></>}
        . The model assigned {risk} risk level. No significant phishing indicators were detected.
      </>
    );
  } else {
    text = (
      <>
        {risk === "HIGH" && <>🚨 <strong>High-confidence phishing detected.</strong> </>}
        {risk === "MEDIUM" && <>⚠️ <strong>Suspicious URL with elevated phishing indicators.</strong> </>}
        {risk === "LOW" && <>⚠️ <strong>Low-confidence phishing signal — proceed with caution.</strong> </>}
        {di?.whois_available && di?.is_new_domain && <> The domain was <strong>recently registered</strong>, a common phishing trait.</>}
        {infra?.tls_ssl_certificate === 0 && <> The SSL certificate is <strong>invalid or self-signed</strong>.</>}
        {di?.whois_available && di?.domain_age && <> Domain age: <strong>{di.domain_age}</strong>.</>}
        {" "}The model flagged this URL with phishing probability. Do not enter credentials on this site.
      </>
    );
  }

  return (
    <Card title="Risk Explanation" icon={<Brain className="w-4 h-4" />}>
      <div className="bg-background/50 border border-border/50 border-l-4 border-l-primary rounded-xl p-4 text-sm leading-relaxed text-foreground/90">
        {text}
      </div>
    </Card>
  );
};


/* ── Infrastructure Signals ─────────────────────────────────────────────── */
const InfrastructureCard = ({ infra }: { infra: InfrastructureFeatures }) => {
  const [open, setOpen] = useState(true);

  const signals: { name: string; value: string; dot: string }[] = [];

  if (infra.tls_ssl_certificate != null) {
    const v = infra.tls_ssl_certificate;
    signals.push({ name: "SSL/TLS Certificate", value: v === 1 ? "Valid ✓" : v === 0 ? "Invalid ✗" : "Unavailable", dot: signalDot(v) });
  }
  if (infra.qty_ip_resolved != null) {
    const v = infra.qty_ip_resolved;
    signals.push({ name: "Resolved IP Addresses", value: v === -1 ? "Unavailable" : String(v), dot: v === -1 ? "bg-slate-500" : v === 0 ? "bg-red-500 shadow-red-500/60" : v >= 3 ? "bg-yellow-500 shadow-yellow-500/60" : "bg-emerald-500 shadow-emerald-500/60" });
  }
  if (infra.qty_nameservers != null) {
    const v = infra.qty_nameservers;
    signals.push({ name: "Nameserver Count", value: v === -1 ? "Unavailable" : String(v), dot: signalDot(v, "positive") });
  }
  if (infra.qty_mx_servers != null) {
    const v = infra.qty_mx_servers;
    signals.push({ name: "MX Records", value: v === -1 ? "Unavailable" : String(v), dot: v === -1 ? "bg-slate-500" : v === 0 ? "bg-yellow-500 shadow-yellow-500/60" : "bg-emerald-500 shadow-emerald-500/60" });
  }
  if (infra.domain_spf != null) {
    const v = infra.domain_spf;
    signals.push({ name: "SPF Record", value: v === 1 ? "Present" : v === 0 ? "Absent" : "Unknown", dot: signalDot(v, "present") });
  }
  if (infra.ttl_hostname != null) {
    const v = infra.ttl_hostname;
    signals.push({ name: "DNS TTL", value: v === -1 ? "Unavailable" : `${v}s`, dot: v === -1 ? "bg-slate-500" : v < 60 ? "bg-yellow-500 shadow-yellow-500/60" : "bg-emerald-500 shadow-emerald-500/60" });
  }
  if (infra.asn_ip != null) {
    const v = infra.asn_ip;
    signals.push({ name: "Autonomous System (ASN)", value: v === -1 ? "Unavailable" : `AS${v}`, dot: v === -1 ? "bg-slate-500" : "bg-emerald-500 shadow-emerald-500/60" });
  }
  if (infra.qty_redirects != null) {
    const v = infra.qty_redirects;
    signals.push({ name: "HTTP Redirects", value: v === -1 ? "Unavailable" : String(v), dot: v === -1 ? "bg-slate-500" : v > 3 ? "bg-red-500 shadow-red-500/60" : v > 1 ? "bg-yellow-500 shadow-yellow-500/60" : "bg-emerald-500 shadow-emerald-500/60" });
  }
  // Google indexing disabled at runtime
  signals.push({ name: "Google Indexing", value: "Runtime Disabled", dot: "bg-slate-500" });

  return (
    <Card
      title="Infrastructure Signals"
      icon={<Lock className="w-4 h-4" />}
      action={
        <button onClick={() => setOpen(o => !o)} className="text-xs text-muted-foreground hover:text-primary transition-colors flex items-center gap-1 font-semibold">
          {open ? <><ChevronUp className="w-3 h-3" /> Hide</> : <><ChevronDown className="w-3 h-3" /> Show</>}
        </button>
      }
    >
      {open && (
        <div className="space-y-2">
          {signals.map(s => (
            <div key={s.name} className="flex items-center justify-between bg-background/50 rounded-xl px-4 py-2.5 border border-border/50">
              <div className="flex items-center gap-3">
                <span className={`w-2 h-2 rounded-full shrink-0 shadow-sm ${s.dot}`} />
                <span className="text-xs text-muted-foreground">{s.name}</span>
              </div>
              <span className="text-sm font-semibold text-foreground">{s.value}</span>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
};

/* ── Domain Intelligence ────────────────────────────────────────────────── */
const DomainIntelligenceCard = ({ domainInfo }: { domainInfo?: DomainInfo | null }) => {
  const di = domainInfo;

  return (
    <Card
      title="Domain Intelligence"
      icon={<Globe className="w-4 h-4" />}
      badge={
        di?.whois_available
          ? di.is_new_domain
            ? <span className="text-[0.65rem] font-bold px-2 py-0.5 rounded-full bg-yellow-500/10 text-yellow-400 border border-yellow-500/30">⚠ New Domain</span>
            : di.domain_age
              ? <span className="text-[0.65rem] font-bold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">{di.domain_age}</span>
              : null
          : null
      }
    >
      {!di || !di.whois_available ? (
        <div className="text-center py-6 text-muted-foreground text-sm bg-background/50 rounded-xl">
          🔍 WHOIS data not available for this domain.
        </div>
      ) : (
        <div className="space-y-4">
          {/* New domain warning */}
          {di.is_new_domain && di.creation_date && (
            <div className="bg-red-500/5 border border-red-500/30 rounded-xl p-3 text-sm text-red-400">
              🚨 <strong>Newly registered domain</strong> — created {di.creation_date}. New domains are a common phishing indicator.
            </div>
          )}
          {/* Expiring soon warning */}
          {di.is_expiring_soon && di.expiration_date && (
            <div className="bg-yellow-500/5 border border-yellow-500/30 rounded-xl p-3 text-sm text-yellow-400">
              ⚠️ <strong>Domain expires soon</strong> — {di.expiration_date}
            </div>
          )}

          {/* Meta grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {di.domain && <MetaItem label="Domain" value={di.domain} />}
            {di.registrar && <MetaItem label="Registrar" value={di.registrar} />}
            {di.org && <MetaItem label="Organisation" value={di.org} />}
            {di.country && <MetaItem label="Country" value={di.country} />}
            {di.creation_date && <MetaItem label="Created" value={di.creation_date} />}
            {di.expiration_date && <MetaItem label="Expires" value={di.expiration_date} />}
            {di.updated_date && <MetaItem label="Last Updated" value={di.updated_date} />}
            {di.domain_age && <MetaItem label="Domain Age" value={di.domain_age} />}
          </div>

          {/* Status tags */}
          {di.status.length > 0 && (
            <div>
              <div className="text-[0.65rem] text-muted-foreground uppercase tracking-wider mb-2">Domain Status</div>
              <div className="flex flex-wrap gap-1.5">
                {di.status.slice(0, 6).map(s => (
                  <span key={s} className="text-xs bg-background/50 text-muted-foreground rounded-md px-2 py-1 border border-border/50">{s}</span>
                ))}
              </div>
            </div>
          )}

          {/* Nameservers */}
          {di.name_servers.length > 0 && (
            <div>
              <div className="text-[0.65rem] text-muted-foreground uppercase tracking-wider mb-2">Name Servers</div>
              <div className="flex flex-wrap gap-1.5">
                {di.name_servers.slice(0, 8).map(ns => (
                  <span key={ns} className="text-xs bg-background/50 text-muted-foreground rounded-md px-2 py-1 border border-border/50">{ns}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </Card>
  );
};



/* ════════════════════════════════════════════════════════════════════════════
   Shared Primitives
   ════════════════════════════════════════════════════════════════════════════ */

const Card = ({ title, icon, badge, action, children }: {
  title: string; icon: React.ReactNode; badge?: React.ReactNode; action?: React.ReactNode; children: React.ReactNode;
}) => (
  <div className="relative group">
    <div className="absolute -inset-0.5 bg-gradient-to-r from-[#19DCF5]/10 to-primary/10 rounded-2xl blur opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
    <div className="relative cyber-card-glow p-5 md:p-6 border border-border/50 hover:border-[#19DCF5]/20 transition-all duration-300">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <span className="text-[#19DCF5]">{icon}</span>
          <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-widest">{title}</h4>
          {badge}
        </div>
        {action}
      </div>
      {children}
    </div>
  </div>
);

const MetaItem = ({ label, value, small }: { label: string; value: string; small?: boolean }) => (
  <div className="bg-background/50 rounded-xl p-3 border border-border/50">
    <div className="text-[0.65rem] text-muted-foreground uppercase tracking-wider">{label}</div>
    <div className={`font-semibold mt-1 text-foreground break-all ${small ? "text-xs" : "text-sm"}`}>{value}</div>
  </div>
);

export default AnalysisResults;
