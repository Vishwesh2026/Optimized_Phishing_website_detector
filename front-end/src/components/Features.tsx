import { Zap, Target, Unlock, MousePointer, Shield, RefreshCw } from "lucide-react";

const features = [
  {
    icon: Zap,
    title: "REAL-TIME DETECTION",
    description: "Instant analysis powered by machine learning algorithms that process URLs in milliseconds",
  },
  {
    icon: Target,
    title: "HIGH ACCURACY",
    description: "Trained on thousands of phishing and legitimate URLs for reliable threat detection",
  },
  {
    icon: Unlock,
    title: "NO BLACKLIST DEPENDENCY",
    description: "Detects new phishing sites that aren't yet in traditional databases or blacklists",
  },
  {
    icon: MousePointer,
    title: "EASY TO USE",
    description: "Simple, intuitive interface - just paste a URL and get instant results",
  },
  {
    icon: Shield,
    title: "FREE & SECURE",
    description: "Completely free to use with no data stored - your privacy is protected",
  },
  {
    icon: RefreshCw,
    title: "ADAPTIVE LEARNING",
    description: "Continuously improving detection algorithms that evolve with new threats",
  },
];

const Features = () => {
  return (
    <section id="features" className="py-20 md:py-28 relative overflow-hidden">
      {/* Base Background */}
      <div className="absolute inset-0 bg-background" />
      
      {/* Circular Pattern Background */}
      <div 
        className="absolute inset-0 opacity-[0.02]"
        style={{
          backgroundImage: `radial-gradient(circle, currentColor 1px, transparent 1px)`,
          backgroundSize: '40px 40px',
        }}
      />
      
      {/* Gradient Overlay */}
      <div className="absolute inset-0 bg-gradient-to-t from-[#19DCF5]/5 via-transparent to-primary/5" />
      
      {/* Animated Wave Lines */}
      <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-[#19DCF5]/30 to-transparent" />
      <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-primary/30 to-transparent" />
      
      {/* Floating Orbs - Different positions */}
      <div className="absolute top-20 left-10 w-64 h-64 bg-[#19DCF5]/6 rounded-full blur-[80px] pointer-events-none animate-pulse" />
      <div className="absolute bottom-20 right-10 w-72 h-72 bg-primary/6 rounded-full blur-[90px] pointer-events-none animate-pulse" style={{ animationDelay: '2s' }} />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-[#19DCF5]/3 rounded-full blur-[120px] pointer-events-none animate-pulse" style={{ animationDelay: '4s' }} />
      
      {/* Overlay for readability */}
      <div className="absolute inset-0 bg-background/40" />
      
      {/* Subtle pattern */}
      <div className="absolute inset-0 cyber-dots opacity-15" />
      
      <div className="container mx-auto px-4 relative z-10 max-w-[1920px]">
        {/* Section Title */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-[#19DCF5]/10 border border-[#19DCF5]/20 rounded-2xl mb-6">
            <Shield className="w-8 h-8 text-[#19DCF5]" />
          </div>
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4 tracking-tight">
            WHY CHOOSE SAFESURF?
          </h2>
          <div className="w-24 h-1 bg-gradient-to-r from-transparent via-[#19DCF5] to-transparent mx-auto mb-4" />
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            Advanced features designed to keep you safe from online threats
          </p>
        </div>

        {/* Features Carousel */}
        <div className="relative overflow-hidden w-full -mx-4 md:-mx-8 lg:-mx-12 xl:-mx-16">
          {/* Gradient Fade on Left */}
          <div className="absolute left-0 top-0 bottom-0 w-40 md:w-48 lg:w-64 bg-gradient-to-r from-background via-background/80 to-transparent z-20 pointer-events-none" />
          
          {/* Gradient Fade on Right */}
          <div className="absolute right-0 top-0 bottom-0 w-40 md:w-48 lg:w-64 bg-gradient-to-l from-background via-background/80 to-transparent z-20 pointer-events-none" />
          
          {/* Carousel Container */}
          <div className="carousel-container flex gap-6 md:gap-8">
            {/* First Set of Cards */}
            {features.map((feature, index) => (
              <div
                key={`first-${feature.title}-${index}`}
                className="group relative flex flex-col flex-shrink-0 w-[380px] md:w-[420px] lg:w-[450px]"
              >
                {/* Card Glow Effect */}
                <div className="absolute -inset-0.5 bg-gradient-to-br from-[#19DCF5]/20 via-primary/20 to-[#19DCF5]/20 rounded-xl blur opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                
                {/* Main Card */}
                <div className="relative cyber-card-glow p-6 md:p-8 border border-border/50 hover:border-[#19DCF5]/40 transition-all duration-300 hover:-translate-y-1 flex flex-col h-full bg-background/60 backdrop-blur-sm">
                  {/* Icon Container */}
                  <div className="relative mb-5 flex-shrink-0">
                    <div className="w-14 h-14 bg-gradient-to-br from-[#19DCF5]/20 to-primary/20 border-2 border-[#19DCF5]/30 rounded-xl flex items-center justify-center group-hover:scale-110 group-hover:border-[#19DCF5]/50 transition-all duration-300 shadow-lg shadow-[#19DCF5]/10">
                      <feature.icon className="w-7 h-7 text-[#19DCF5] transition-colors duration-300" />
                    </div>
                    <div className="absolute inset-0 bg-[#19DCF5]/20 blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-xl" />
                  </div>
                  
                  {/* Content */}
                  <div className="flex flex-col flex-grow">
                    <h3 className="text-lg md:text-xl font-bold text-foreground mb-3 tracking-tight flex items-center gap-2 flex-shrink-0">
                      {feature.title}
                      <span className="w-6 h-0.5 bg-[#19DCF5] opacity-50" />
                    </h3>
                    <p className="text-muted-foreground text-sm leading-relaxed flex-grow">
                      {feature.description}
                    </p>
                  </div>
                </div>
              </div>
            ))}
            
            {/* Duplicate Set for Seamless Loop */}
            {features.map((feature, index) => (
              <div
                key={`second-${feature.title}-${index}`}
                className="group relative flex flex-col flex-shrink-0 w-[380px] md:w-[420px] lg:w-[450px]"
              >
                {/* Card Glow Effect */}
                <div className="absolute -inset-0.5 bg-gradient-to-br from-[#19DCF5]/20 via-primary/20 to-[#19DCF5]/20 rounded-xl blur opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                
                {/* Main Card */}
                <div className="relative cyber-card-glow p-6 md:p-8 border border-border/50 hover:border-[#19DCF5]/40 transition-all duration-300 hover:-translate-y-1 flex flex-col h-full bg-background/60 backdrop-blur-sm">
                  {/* Icon Container */}
                  <div className="relative mb-5 flex-shrink-0">
                    <div className="w-14 h-14 bg-gradient-to-br from-[#19DCF5]/20 to-primary/20 border-2 border-[#19DCF5]/30 rounded-xl flex items-center justify-center group-hover:scale-110 group-hover:border-[#19DCF5]/50 transition-all duration-300 shadow-lg shadow-[#19DCF5]/10">
                      <feature.icon className="w-7 h-7 text-[#19DCF5] transition-colors duration-300" />
                    </div>
                    <div className="absolute inset-0 bg-[#19DCF5]/20 blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-xl" />
                  </div>
                  
                  {/* Content */}
                  <div className="flex flex-col flex-grow">
                    <h3 className="text-lg md:text-xl font-bold text-foreground mb-3 tracking-tight flex items-center gap-2 flex-shrink-0">
                      {feature.title}
                      <span className="w-6 h-0.5 bg-[#19DCF5] opacity-50" />
                    </h3>
                    <p className="text-muted-foreground text-sm leading-relaxed flex-grow">
                      {feature.description}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
        
        <style>{`
          @keyframes scroll {
            0% {
              transform: translateX(0) translateZ(0);
            }
            100% {
              transform: translateX(-50%) translateZ(0);
            }
          }
          
          .carousel-container {
            animation: scroll 30s linear infinite;
            will-change: transform;
            transform: translateZ(0);
          }
          
          .carousel-container:hover {
            animation-play-state: paused;
          }
        `}</style>
      </div>
    </section>
  );
};

export default Features;
