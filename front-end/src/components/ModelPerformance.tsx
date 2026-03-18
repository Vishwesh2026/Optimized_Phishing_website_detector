import { useState, useEffect } from "react";
import { Server, BarChart3 } from "lucide-react";
import { fetchMetrics } from "@/services/api";
import type { MetricsResponse } from "@/types/analysis";

const ModelPerformance = () => {
  const [metrics, setMetrics] = useState<MetricsResponse | null>(null);

  useEffect(() => {
    fetchMetrics().then(setMetrics).catch(() => {/* silently hide */});
  }, []);

  if (!metrics) return null;

  const bars = [
    { name: "Accuracy",  val: metrics.accuracy },
    { name: "Precision", val: metrics.precision },
    { name: "Recall",    val: metrics.recall },
    { name: "F1 Score",  val: metrics.f1 ?? metrics.f1_score },
    { name: "ROC-AUC",   val: metrics.roc_auc },
  ].filter(b => b.val != null);

  const cm = metrics.confusion_matrix;

  return (
    <section id="model-performance" className="py-20 md:py-28 relative overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-b from-background via-background/95 to-background" />
      <div className="absolute inset-0 cyber-dots opacity-20" />

      {/* Glowing Orbs */}
      <div className="absolute top-1/3 right-1/4 w-96 h-96 bg-primary/5 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute bottom-1/3 left-1/4 w-96 h-96 bg-[#19DCF5]/5 rounded-full blur-[100px] pointer-events-none" />

      <div className="container mx-auto px-4 relative z-10">
        <div className="max-w-3xl mx-auto">
          {/* Section Title */}
          <div className="text-center mb-12">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-primary/10 border border-primary/20 rounded-2xl mb-6">
              <BarChart3 className="w-8 h-8 text-primary" />
            </div>
            <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4 tracking-tight">
              MODEL PERFORMANCE
            </h2>
            <div className="w-24 h-1 bg-gradient-to-r from-transparent via-primary to-transparent mx-auto mb-4" />
            <p className="text-muted-foreground text-lg">
              Training metrics evaluated on the held-out test set
            </p>
          </div>

          {/* Card */}
          <div className="relative group">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-[#19DCF5]/10 to-primary/10 rounded-2xl blur opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <div className="relative cyber-card-glow p-5 md:p-6 border border-border/50 hover:border-[#19DCF5]/20 transition-all duration-300">
              <div className="flex items-center gap-2 mb-4">
                <span className="text-[#19DCF5]"><Server className="w-4 h-4" /></span>
                <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-widest">
                  Ensemble Model Metrics
                </h4>
              </div>

              {/* Metric bars */}
              <div className="space-y-3">
                {bars.map(b => {
                  const pct = Math.round((b.val || 0) * 100);
                  return (
                    <div key={b.name} className="space-y-1">
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">{b.name}</span>
                        <span className="font-bold text-foreground">{pct}%</span>
                      </div>
                      <div className="h-2 bg-background/50 rounded-full overflow-hidden border border-border/30">
                        <div className="h-full rounded-full bg-gradient-to-r from-primary to-primary/80 transition-all duration-1000" style={{ width: `${pct}%` }} />
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Meta grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-4">
                <MetaItem label="Model File" value={metrics.model_file || metrics.model || "—"} small />
                <MetaItem label="Dataset Size" value={(metrics.dataset_size || 0).toLocaleString()} />
                <MetaItem label="Features" value={String(metrics.feature_count || metrics.n_features || 111)} />
                <MetaItem label="Trained At" value={metrics.trained_at ? metrics.trained_at.replace("T", " ") : "—"} small />
              </div>

              {/* Confusion Matrix */}
              {cm && cm.length === 2 && (
                <div className="mt-4">
                  <div className="text-[0.65rem] text-muted-foreground uppercase tracking-wider mb-2">Confusion Matrix</div>
                  <div className="grid grid-cols-2 gap-2 max-w-[280px]">
                    {[
                      { v: cm[0][0], l: "True Negative",  cls: "border-emerald-500/30" },
                      { v: cm[0][1], l: "False Positive",  cls: "border-red-500/30" },
                      { v: cm[1][0], l: "False Negative",  cls: "border-yellow-500/30" },
                      { v: cm[1][1], l: "True Positive",   cls: "border-emerald-500/30" },
                    ].map(c => (
                      <div key={c.l} className={`bg-background/50 rounded-lg p-3 text-center border ${c.cls}`}>
                        <div className="text-lg font-bold text-foreground">{c.v.toLocaleString()}</div>
                        <div className="text-[0.6rem] text-muted-foreground mt-0.5">{c.l}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="text-center text-[0.7rem] text-muted-foreground mt-4 pt-3 border-t border-border/30">
                ⚠ Training Metrics — Not Live Accuracy &nbsp;|&nbsp; Evaluated on held-out test set
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

/* ── Shared Primitive ──────────────────────────────────────────────────── */
const MetaItem = ({ label, value, small }: { label: string; value: string; small?: boolean }) => (
  <div className="bg-background/50 rounded-xl p-3 border border-border/50">
    <div className="text-[0.65rem] text-muted-foreground uppercase tracking-wider">{label}</div>
    <div className={`font-semibold mt-1 text-foreground break-all ${small ? "text-xs" : "text-sm"}`}>{value}</div>
  </div>
);

export default ModelPerformance;
