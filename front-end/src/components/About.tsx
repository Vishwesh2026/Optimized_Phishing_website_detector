import { Brain, Target, Zap } from "lucide-react";
import WebIcon from "@/assets/WebIcon.png";

const About = () => {
  const features = [
    {
      icon: Brain,
      title: "AI-Powered",
      description: "Advanced machine learning algorithms for accurate detection",
    },
    {
      icon: Zap,
      title: "Real-Time",
      description: "Instant analysis and results in seconds",
    },
    {
      icon: Target,
      title: "Precise",
      description: "High accuracy in identifying phishing threats",
    },
  ];

  return (
    <section id="about" className="py-20 md:py-28 relative overflow-hidden">
      {/* Gradient Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-background via-background to-background/95" />
      
      {/* Animated Gradient Overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-[#19DCF5]/10 via-transparent to-primary/10 animate-pulse" />
      
      {/* Grid Pattern Background */}
      <div 
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage: `
            linear-gradient(to right, currentColor 1px, transparent 1px),
            linear-gradient(to bottom, currentColor 1px, transparent 1px)
          `,
          backgroundSize: '50px 50px',
        }}
      />
      
      {/* Background Elements */}
      <div className="absolute inset-0 cyber-dots opacity-20" />
      
      {/* Animated Glowing Orbs */}
      <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-[#19DCF5]/10 rounded-full blur-[100px] pointer-events-none animate-pulse" />
      <div className="absolute bottom-1/4 left-1/4 w-96 h-96 bg-primary/10 rounded-full blur-[100px] pointer-events-none animate-pulse" style={{ animationDelay: '1s' }} />
      <div className="absolute top-1/2 left-1/2 w-80 h-80 bg-[#19DCF5]/5 rounded-full blur-[120px] pointer-events-none animate-pulse" style={{ animationDelay: '2s' }} />
      
      {/* Radial Gradient Overlay for depth */}
      <div 
        className="absolute inset-0 pointer-events-none"
        style={{
          background: 'radial-gradient(circle at 50% 50%, rgba(25, 220, 245, 0.05) 0%, transparent 70%)'
        }}
      />
      
      <div className="container mx-auto px-4 relative z-10">
        <div className="max-w-6xl mx-auto">
          {/* Section Title */}
          <div className="text-center mb-16">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-[#19DCF5]/10 border border-[#19DCF5]/20 rounded-2xl mb-6">
              <img 
                src={WebIcon} 
                alt="SafeSurf Logo" 
                className="w-8 h-8 rounded-full object-cover" 
              />
            </div>
            <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4 tracking-tight">
              ABOUT SAFESURF
            </h2>
            <div className="w-24 h-1 bg-gradient-to-r from-transparent via-[#19DCF5] to-transparent mx-auto" />
          </div>

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
            {/* Mission Card - Takes 2 columns on large screens */}
            <div className="lg:col-span-2">
              <div className="relative group">
                {/* Card Glow Effect */}
                <div className="absolute -inset-0.5 bg-gradient-to-r from-[#19DCF5]/20 to-primary/20 rounded-2xl blur opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                
                {/* Main Card */}
                <div className="relative cyber-card-glow p-8 md:p-12 h-full border border-border/50 hover:border-[#19DCF5]/30 transition-all duration-300">
                  {/* Icon Badge */}
                  <div className="flex items-start gap-6 mb-6">
                    <div className="relative shrink-0">
                      <div className="w-14 h-14 bg-gradient-to-br from-[#19DCF5]/20 to-primary/20 border border-[#19DCF5]/30 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300 overflow-hidden">
                        <img 
                          src={WebIcon} 
                          alt="SafeSurf Logo" 
                          className="w-10 h-10 rounded-full object-cover" 
                        />
                      </div>
                      <div className="absolute inset-0 bg-[#19DCF5]/20 blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-xl" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold text-foreground mb-3 tracking-tight flex items-center gap-2">
                        OUR MISSION
                        <span className="w-8 h-0.5 bg-[#19DCF5] opacity-50" />
                      </h3>
                      <p className="text-muted-foreground leading-relaxed">
                        SafeSurf is a machine learning-based cybersecurity tool developed to combat the rising threat of phishing attacks. This tool uses advanced ML algorithms including Random Forest, XGBoost, and SVM to analyze website features and protect users from online fraud. Our goal is to make the internet safer for everyone by providing instant, accurate phishing detection.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Technology Stack Card */}
            <div className="lg:col-span-1">
              <div className="relative group h-full">
                <div className="absolute -inset-0.5 bg-gradient-to-b from-[#19DCF5]/20 to-primary/20 rounded-2xl blur opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                <div className="relative cyber-card-glow p-8 h-full border border-border/50 hover:border-[#19DCF5]/30 transition-all duration-300 flex flex-col">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="w-10 h-10 bg-[#19DCF5]/10 border border-[#19DCF5]/20 rounded-lg flex items-center justify-center">
                      <Brain className="w-5 h-5 text-[#19DCF5]" />
                    </div>
                    <h3 className="text-xl font-semibold text-foreground tracking-tight">
                      TECHNOLOGY
                    </h3>
                  </div>
                  <div className="space-y-3 flex-1">
                    {["Random Forest", "XGBoost", "SVM", "Feature Analysis"].map((tech, idx) => (
                      <div key={tech} className="flex items-center gap-2 group/item">
                        <div className="w-1.5 h-1.5 bg-[#19DCF5] rounded-full opacity-60 group-hover/item:opacity-100 transition-opacity" />
                        <span className="text-muted-foreground text-sm">{tech}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-stretch">
            {features.map((feature, index) => (
              <div
                key={feature.title}
                className="group relative flex flex-col h-full"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className="absolute -inset-0.5 bg-gradient-to-r from-[#19DCF5]/10 to-primary/10 rounded-xl blur opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                <div className="relative cyber-card p-6 border border-border/50 hover:border-[#19DCF5]/30 transition-all duration-300 hover:-translate-y-1 flex flex-col h-full">
                  <div className="w-12 h-12 bg-gradient-to-br from-[#19DCF5]/20 to-primary/20 border border-[#19DCF5]/30 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300 flex-shrink-0">
                    <feature.icon className="w-6 h-6 text-[#19DCF5]" />
                  </div>
                  <h4 className="text-xl font-semibold text-foreground mb-2 tracking-tight flex-shrink-0">
                    {feature.title}
                  </h4>
                  <p className="text-muted-foreground text-sm leading-relaxed flex-grow">
                    {feature.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default About;
