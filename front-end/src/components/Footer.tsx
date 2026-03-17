import { Github, ExternalLink, Mail, Shield } from "lucide-react";
import WebIcon from "@/assets/WebIcon.png";

const Footer = () => {
  const handleNavClick = (href: string) => {
    const element = document.querySelector(href);
    element?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <footer id="contact" className="relative bg-gradient-to-b from-background to-background/95 border-t border-border/50 overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 cyber-dots opacity-10" />
      
      {/* Gradient Overlay */}
      <div className="absolute inset-0 bg-gradient-to-t from-primary/5 via-transparent to-transparent" />
      
      <div className="container mx-auto px-4 py-16 md:py-20 relative z-10">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12 mb-12">
          {/* Logo & Description */}
          <div className="lg:col-span-2">
            <div className="flex items-center gap-3 mb-6 group">
              <div className="relative">
                <img 
                  src={WebIcon} 
                  alt="SafeSurf Logo" 
                  className="w-10 h-10 md:w-12 md:h-12 rounded-full object-cover transition-transform duration-300 group-hover:scale-110" 
                />
                <div className="absolute inset-0 bg-[#19DCF5]/20 blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-full" />
              </div>
              <span className="text-2xl md:text-3xl font-bold text-foreground tracking-tight bg-gradient-to-r from-foreground to-foreground/80 bg-clip-text">
                SafeSurf
              </span>
            </div>
            <p className="text-muted-foreground text-sm md:text-base leading-relaxed max-w-md mb-6">
              AI-powered phishing detection to keep you safe online. An academic project by computer science students at Aditya College of Engineering & Technology.
            </p>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Shield className="w-4 h-4 text-[#19DCF5]" />
              <span>Protecting users from phishing attacks since 2025</span>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="font-bold text-foreground mb-6 tracking-wide uppercase text-sm relative inline-block pb-2 after:absolute after:bottom-0 after:left-0 after:w-12 after:h-0.5 after:bg-[#19DCF5]">
              Quick Links
            </h4>
            <ul className="space-y-3">
              {[
                { href: "#how-it-works", label: "How It Works" },
                { href: "#about", label: "About" },
                { href: "#url-checker", label: "URL Checker" },
              ].map((link) => (
                <li key={link.href}>
                  <a
                    href={link.href}
                    onClick={(e) => {
                      e.preventDefault();
                      handleNavClick(link.href);
                    }}
                    className="text-muted-foreground hover:text-[#19DCF5] text-sm transition-all duration-300 flex items-center gap-2 group/link hover:translate-x-1"
                  >
                    <ExternalLink className="w-3.5 h-3.5 opacity-0 group-hover/link:opacity-100 transition-opacity duration-300" />
                    <span className="group-hover/link:translate-x-0 transition-transform duration-300">{link.label}</span>
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Connect */}
          <div>
            <h4 className="font-bold text-foreground mb-6 tracking-wide uppercase text-sm relative inline-block pb-2 after:absolute after:bottom-0 after:left-0 after:w-12 after:h-0.5 after:bg-[#19DCF5]">
              Connect
            </h4>
            <p className="text-muted-foreground text-sm mb-4 leading-relaxed">
              Follow us for updates and contributions
            </p>
            <div className="flex items-center gap-3">
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="group relative w-11 h-11 bg-secondary/50 hover:bg-[#19DCF5] border border-border hover:border-[#19DCF5] rounded-xl flex items-center justify-center transition-all duration-300 hover:scale-110 hover:shadow-lg hover:shadow-[#19DCF5]/20"
              >
                <Github className="w-5 h-5 text-muted-foreground group-hover:text-white transition-colors duration-300" />
              </a>
              <a
                href="mailto:contact@safesurf.ai"
                className="group relative w-11 h-11 bg-secondary/50 hover:bg-[#19DCF5] border border-border hover:border-[#19DCF5] rounded-xl flex items-center justify-center transition-all duration-300 hover:scale-110 hover:shadow-lg hover:shadow-[#19DCF5]/20"
              >
                <Mail className="w-5 h-5 text-muted-foreground group-hover:text-white transition-colors duration-300" />
              </a>
            </div>
          </div>
        </div>

        {/* Divider */}
        <div className="border-t border-border/50 pt-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-muted-foreground text-sm text-center md:text-left">
              © 2025 <span className="text-[#19DCF5] font-semibold">SafeSurf</span>. Academic Project - Aditya College of Engineering & Technology
            </p>
            <p className="text-muted-foreground/70 text-xs text-center md:text-right max-w-md">
              For educational purposes. Always verify suspicious websites through multiple methods.
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
