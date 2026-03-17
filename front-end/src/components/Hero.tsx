import { ChevronDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import WebIcon from "@/assets/WebIcon.png";
import HeroBgVideo from "@/assets/Herobg.mp4";

const Hero = () => {
  const handleScrollToChecker = () => {
    const element = document.querySelector("#url-checker");
    element?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <section
      id="home"
      className="relative min-h-screen flex items-center justify-center overflow-hidden bg-hero-gradient"
    >
      {/* Background Video */}
      <video
        autoPlay
        loop
        muted
        playsInline
        className="absolute inset-0 w-full h-full object-cover z-0"
      >
        <source src={HeroBgVideo} type="video/mp4" />
      </video>

      {/* Video Overlay */}
      <div className="absolute inset-0 bg-background/40 z-[1]" />

      {/* Animated Background Pattern */}
      <div className="absolute inset-0 hero-pattern animate-grid-flow opacity-60 z-[2]" />
      
      {/* Glowing orbs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none z-[2]">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-[100px] animate-pulse-glow" />
        <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-accent/10 rounded-full blur-[120px] animate-pulse-glow" style={{ animationDelay: "1s" }} />
        <div className="absolute top-1/2 right-1/3 w-64 h-64 bg-primary/15 rounded-full blur-[80px] animate-pulse-glow" style={{ animationDelay: "0.5s" }} />
      </div>

      <div className="container mx-auto px-4 relative z-[3]">
        <div className="flex flex-col items-center text-center max-w-4xl mx-auto">
          {/* Floating Logo Icon */}
          <div className="relative mb-8 animate-float">
            <div className="absolute inset-0 bg-primary/40 blur-2xl rounded-full" />
            <div className="relative p-4 rounded-2xl bg-secondary/50 backdrop-blur-sm border border-border">
              <img 
                src={WebIcon} 
                alt="SafeSurf Logo" 
                className="w-16 h-16 md:w-20 md:h-20 rounded-full object-cover" 
              />
            </div>
          </div>

          {/* Main Heading */}
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-foreground mb-6 leading-tight animate-slide-up tracking-tight">
            PROTECT YOURSELF FROM{" "}
            <span className="relative inline-block">
              <span className="relative z-10 text-accent">PHISHING ATTACKS</span>
              <span className="absolute bottom-1 left-0 right-0 h-3 bg-accent/20 -z-0" />
            </span>
          </h1>

          {/* Subheading */}
          <p className="text-lg md:text-xl text-muted-foreground mb-10 max-w-2xl animate-slide-up leading-relaxed" style={{ animationDelay: "0.1s" }}>
            Real-time AI-powered phishing detection. Check any URL instantly and browse the web with confidence.
          </p>

          {/* CTA Button */}
          <Button
            size="lg"
            onClick={handleScrollToChecker}
            className="bg-primary hover:bg-primary/90 text-primary-foreground font-semibold px-8 py-6 text-lg rounded-xl transition-all duration-300 hover:scale-105 animate-slide-up hover:shadow-glow"
            style={{ animationDelay: "0.2s" }}
          >
            <img 
              src={WebIcon} 
              alt="SafeSurf Logo" 
              className="w-5 h-5 mr-2 rounded-full object-cover" 
            />
            CHECK URL NOW
          </Button>

          {/* Trust Indicators */}
          <div className="flex flex-wrap items-center justify-center gap-6 mt-12 text-muted-foreground text-sm animate-slide-up" style={{ animationDelay: "0.3s" }}>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-success rounded-full animate-pulse" />
              <span className="tracking-wide">Free to Use</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-success rounded-full animate-pulse" />
              <span className="tracking-wide">No Data Stored</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-success rounded-full animate-pulse" />
              <span className="tracking-wide">Instant Results</span>
            </div>
          </div>
        </div>
      </div>

      {/* Scroll Indicator */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce z-[3]">
        <ChevronDown className="w-8 h-8 text-muted-foreground" />
      </div>
    </section>
  );
};

export default Hero;
