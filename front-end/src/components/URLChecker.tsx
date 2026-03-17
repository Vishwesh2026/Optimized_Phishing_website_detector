import { useState } from "react";
import { Shield, Loader2, Link as LinkIcon, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { analyzeUrl } from "@/services/api";
import AnalysisResults from "@/components/AnalysisResults";
import type { AnalyzeResponse } from "@/types/analysis";

const URLChecker = () => {
  const [url, setUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState("");

  const isValidUrl = (urlString: string): boolean => {
    try {
      const u = new URL(urlString);
      return u.protocol === "http:" || u.protocol === "https:";
    } catch {
      return false;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setResult(null);

    const trimmedUrl = url.trim();

    if (!trimmedUrl) {
      setError("Please enter a URL to check");
      return;
    }

    if (!isValidUrl(trimmedUrl)) {
      setError("Please enter a valid URL starting with http:// or https://");
      return;
    }

    setIsLoading(true);

    try {
      const analysisResult = await analyzeUrl(trimmedUrl);
      setResult(analysisResult);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to analyze URL. Please check your connection and try again."
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setUrl("");
    setResult(null);
    setError("");
  };

  return (
    <section id="url-checker" className="py-20 md:py-28 relative overflow-hidden">
      {/* Background Elements */}
      <div className="absolute inset-0 bg-gradient-to-b from-background via-background/95 to-background" />
      <div className="absolute inset-0 cyber-dots opacity-20" />
      
      {/* Glowing Orbs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#19DCF5]/5 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-primary/5 rounded-full blur-[100px] pointer-events-none" />
      
      <div className="container mx-auto px-4 relative z-10">
        <div className="max-w-3xl mx-auto">
          {/* Section Title */}
          <div className="text-center mb-12">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-[#19DCF5]/10 border border-[#19DCF5]/20 rounded-2xl mb-6">
              <Shield className="w-8 h-8 text-[#19DCF5]" />
            </div>
            <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4 tracking-tight">
              ENTER URL TO CHECK
            </h2>
            <div className="w-24 h-1 bg-gradient-to-r from-transparent via-[#19DCF5] to-transparent mx-auto mb-4" />
            <p className="text-muted-foreground text-lg">
              Paste any website URL below and our AI will analyze it for phishing threats
            </p>
          </div>

          {/* URL Input Card */}
          <div className="relative group">
            {/* Card Glow Effect */}
            <div className="absolute -inset-0.5 bg-gradient-to-r from-[#19DCF5]/20 to-primary/20 rounded-2xl blur opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            
            <div className="relative cyber-card-glow p-6 md:p-8 border border-border/50 hover:border-[#19DCF5]/30 transition-all duration-300">
              <form onSubmit={handleSubmit} className="space-y-5">
                <div className="relative">
                  <div className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground z-10">
                    <LinkIcon className="w-5 h-5" />
                  </div>
                  <Input
                    type="text"
                    placeholder="Enter website URL (https://example.com)"
                    value={url}
                    onChange={(e) => {
                      setUrl(e.target.value);
                      setError("");
                    }}
                    disabled={isLoading}
                    className={`pl-12 pr-4 py-6 text-lg rounded-xl bg-background/50 backdrop-blur-sm border-2 text-foreground placeholder:text-muted-foreground transition-all duration-300 ${
                      error
                        ? "border-destructive focus:border-destructive focus:ring-destructive/20"
                        : "border-border focus:border-[#19DCF5] focus:ring-[#19DCF5]/20 focus:shadow-lg focus:shadow-[#19DCF5]/20"
                    }`}
                  />
                </div>

                {error && (
                  <div className="bg-destructive/10 border border-destructive/30 rounded-xl p-3 animate-fade-in">
                    <p className="text-destructive text-sm flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4 shrink-0" />
                      {error}
                    </p>
                  </div>
                )}

                <Button
                  type="submit"
                  disabled={isLoading}
                  className="w-full py-6 text-lg font-semibold rounded-xl bg-gradient-to-r from-primary to-primary/90 hover:from-primary/90 hover:to-primary text-primary-foreground transition-all duration-300 hover:shadow-lg hover:shadow-primary/30 hover:scale-[1.02] tracking-wide relative overflow-hidden group/btn"
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-[#19DCF5]/20 to-transparent opacity-0 group-hover/btn:opacity-100 transition-opacity duration-300" />
                  <span className="relative z-10 flex items-center justify-center">
                    {isLoading ? (
                      <>
                        <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                        ANALYZING...
                      </>
                    ) : (
                      <>
                        <Shield className="w-5 h-5 mr-2" />
                        ANALYZE URL
                      </>
                    )}
                  </span>
                </Button>
              </form>
            </div>
          </div>

          {/* Results Display */}
          {result && (
            <div className="mt-8 animate-slide-up">
              <AnalysisResults result={result} onReset={handleReset} />
            </div>
          )}
        </div>
      </div>
    </section>
  );
};

export default URLChecker;
