import { Search, Brain, ShieldCheck } from "lucide-react";

const steps = [
  {
    icon: Search,
    title: "ENTER URL",
    description: "Paste any website URL you want to check into our secure analyzer",
  },
  {
    icon: Brain,
    title: "AI ANALYSIS",
    description: "Our machine learning model analyzes URL patterns, domain features, and security indicators",
  },
  {
    icon: ShieldCheck,
    title: "INSTANT RESULTS",
    description: "Get real-time classification: legitimate or phishing, with confidence scores",
  },
];

const HowItWorks = () => {
  return (
    <section id="how-it-works" className="py-20 md:py-28 relative overflow-hidden">
      {/* Base Background */}
      <div className="absolute inset-0 bg-background" />
      
      {/* Diagonal Stripe Pattern */}
      <div 
        className="absolute inset-0 opacity-[0.04]"
        style={{
          backgroundImage: `repeating-linear-gradient(
            45deg,
            currentColor 0px,
            currentColor 2px,
            transparent 2px,
            transparent 20px
          )`,
        }}
      />
      
      {/* Vertical Gradient Flow */}
      <div className="absolute inset-0 bg-gradient-to-b from-[#19DCF5]/8 via-transparent to-primary/8" />
      
      {/* Horizontal Accent Lines */}
      <div className="absolute top-1/4 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#19DCF5]/20 to-transparent" />
      <div className="absolute bottom-1/4 left-0 right-0 h-px bg-gradient-to-r from-transparent via-primary/20 to-transparent" />
      
      {/* Animated Flowing Orbs - Different style from About */}
      <div className="absolute top-0 left-1/3 w-72 h-72 bg-[#19DCF5]/8 rounded-full blur-[80px] pointer-events-none animate-pulse" />
      <div className="absolute bottom-0 right-1/3 w-80 h-80 bg-primary/8 rounded-full blur-[90px] pointer-events-none animate-pulse" style={{ animationDelay: '1.5s' }} />
      <div className="absolute top-1/2 right-0 w-64 h-64 bg-[#19DCF5]/6 rounded-full blur-[70px] pointer-events-none animate-pulse" style={{ animationDelay: '3s' }} />
      
      {/* Geometric Shapes */}
      <div className="absolute top-10 right-10 w-32 h-32 border border-[#19DCF5]/10 rotate-45 pointer-events-none" />
      <div className="absolute bottom-20 left-20 w-24 h-24 border border-primary/10 rotate-12 pointer-events-none" />
      
      {/* Overlay for readability */}
      <div className="absolute inset-0 bg-background/50 z-[1]" />
      
      {/* Subtle pattern */}
      <div className="absolute inset-0 cyber-dots opacity-15 z-[2]" />
      
      <div className="container mx-auto px-4 relative z-[3]">
        {/* Section Title */}
        <div className="text-center mb-20">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-[#19DCF5]/10 border border-[#19DCF5]/20 rounded-2xl mb-6">
            <ShieldCheck className="w-8 h-8 text-[#19DCF5]" />
          </div>
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4 tracking-tight">
            HOW SAFESURF WORKS
          </h2>
          <div className="w-24 h-1 bg-gradient-to-r from-transparent via-[#19DCF5] to-transparent mx-auto mb-4" />
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            Three simple steps to protect yourself from phishing websites
          </p>
        </div>

        {/* Steps Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 md:gap-12 max-w-6xl mx-auto items-stretch">
          {steps.map((step, index) => (
            <div
              key={step.title}
              className="group relative flex flex-col"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              {/* Card Glow Effect */}
              <div className="absolute -inset-0.5 bg-gradient-to-r from-[#19DCF5]/20 to-primary/20 rounded-2xl blur opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
              
              <div className="relative cyber-card p-8 md:p-10 border border-border/50 hover:border-[#19DCF5]/50 transition-all duration-300 hover:-translate-y-2 hover:shadow-xl hover:shadow-[#19DCF5]/10 bg-background/40 backdrop-blur-sm flex flex-col h-full">
                {/* Step Number Badge */}
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 w-10 h-10 bg-gradient-to-br from-[#19DCF5] to-primary rounded-full flex items-center justify-center border-2 border-background shadow-lg z-20">
                  <span className="text-sm font-bold text-white">{index + 1}</span>
                </div>

                {/* Connector Line */}
                {index < steps.length - 1 && (
                  <div className="hidden md:block absolute top-1/2 -right-6 w-12 h-0.5 z-10">
                    <div className="absolute inset-0 bg-gradient-to-r from-[#19DCF5]/50 to-transparent" />
                    <div className="absolute right-0 top-1/2 -translate-y-1/2 w-3 h-3 bg-[#19DCF5] rounded-full border-2 border-background shadow-lg shadow-[#19DCF5]/30 animate-pulse" />
                  </div>
                )}

                {/* Icon Container */}
                <div className="relative mb-6 mt-2 flex-shrink-0">
                  <div className="w-20 h-20 bg-gradient-to-br from-[#19DCF5]/20 to-primary/20 border-2 border-[#19DCF5]/30 rounded-2xl flex items-center justify-center group-hover:scale-110 group-hover:border-[#19DCF5]/50 transition-all duration-300 shadow-lg shadow-[#19DCF5]/10">
                    <step.icon className="w-10 h-10 text-[#19DCF5] transition-colors duration-300" />
                  </div>
                  <div className="absolute inset-0 bg-[#19DCF5]/20 blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-2xl" />
                </div>

                {/* Content */}
                <div className="flex flex-col flex-grow">
                  <h3 className="text-xl font-bold text-foreground mb-4 tracking-tight flex items-center gap-2 flex-shrink-0">
                    {step.title}
                    <span className="w-6 h-0.5 bg-[#19DCF5] opacity-50" />
                  </h3>
                  <p className="text-muted-foreground leading-relaxed flex-grow">
                    {step.description}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;
