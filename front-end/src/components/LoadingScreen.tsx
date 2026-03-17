import { useEffect, useState } from "react";
import WebIcon from "@/assets/WebIcon.png";

const LoadingScreen = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [isFading, setIsFading] = useState(false);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    // Minimum loading time for smooth experience
    const minLoadTime = 2000; // 2 seconds for better progress animation
    const startTime = Date.now();
    const progressInterval = 50; // Update every 50ms for smooth animation

    // Progress animation
    const progressTimer = setInterval(() => {
      const elapsed = Date.now() - startTime;
      const progressPercent = Math.min(100, Math.floor((elapsed / minLoadTime) * 100));
      setProgress(progressPercent);
    }, progressInterval);

    // Check if page is loaded
    const handleLoad = () => {
      const elapsed = Date.now() - startTime;
      const remaining = Math.max(0, minLoadTime - elapsed);

      // Ensure progress reaches 100%
      setProgress(100);

      setTimeout(() => {
        clearInterval(progressTimer);
        setIsFading(true);
        // Remove from DOM after fade animation
        setTimeout(() => {
          setIsLoading(false);
        }, 600); // Match fade-out duration
      }, remaining);
    };

    // If page is already loaded
    if (document.readyState === "complete") {
      handleLoad();
    } else {
      window.addEventListener("load", handleLoad);
      // Fallback timeout
      setTimeout(handleLoad, 3000);
    }

    return () => {
      clearInterval(progressTimer);
      window.removeEventListener("load", handleLoad);
    };
  }, []);

  if (!isLoading) return null;

  return (
    <>
      <style>{`
        @keyframes smoothPulse {
          0%, 100% { opacity: 0.4; transform: scale(1); }
          50% { opacity: 0.8; transform: scale(1.05); }
        }
        
        @keyframes smoothRotate {
          from { transform: rotate(0deg) translateZ(0); }
          to { transform: rotate(360deg) translateZ(0); }
        }
        
        @keyframes smoothFloat {
          0%, 100% { transform: translateY(0px) translateZ(0); }
          50% { transform: translateY(-10px) translateZ(0); }
        }
        
        @keyframes smoothScale {
          0%, 100% { transform: scale(1) translateZ(0); }
          50% { transform: scale(1.1) translateZ(0); }
        }
        
        @keyframes dotBounce {
          0%, 80%, 100% { transform: translateY(0) translateZ(0); opacity: 0.5; }
          40% { transform: translateY(-8px) translateZ(0); opacity: 1; }
        }
        
        @keyframes ringExpand {
          0% { transform: scale(0.8) translateZ(0); opacity: 0.6; }
          50% { transform: scale(1.2) translateZ(0); opacity: 0.3; }
          100% { transform: scale(1.5) translateZ(0); opacity: 0; }
        }
        
        .progress-ring {
          transform: rotate(-90deg);
          transform-origin: center;
        }
        
        .progress-ring-circle {
          transition: stroke-dashoffset 0.1s ease-out;
          transform: translateZ(0);
          will-change: stroke-dashoffset;
        }
        
        .loading-screen {
          will-change: opacity;
          transform: translateZ(0);
          backface-visibility: hidden;
        }
        
        .logo-container {
          will-change: transform;
          transform: translateZ(0);
        }
        
        .logo-float {
          animation: smoothFloat 2s ease-in-out infinite;
          will-change: transform;
          transform: translateZ(0);
        }
        
        .ring-pulse {
          animation: smoothPulse 2s ease-in-out infinite;
          will-change: opacity, transform;
          transform: translateZ(0);
        }
        
        .ring-expand {
          animation: ringExpand 2s ease-in-out infinite;
          will-change: transform, opacity;
          transform: translateZ(0);
        }
        
        .orb-glow {
          animation: smoothPulse 3s ease-in-out infinite;
          will-change: opacity;
          transform: translateZ(0);
        }
        
        .dot-animate {
          animation: dotBounce 1.4s ease-in-out infinite;
          will-change: transform, opacity;
          transform: translateZ(0);
        }
      `}</style>
      
      <div
        className={`loading-screen fixed inset-0 z-[9999] flex items-center justify-center bg-background transition-opacity duration-600 ease-out ${
          isFading ? "opacity-0" : "opacity-100"
        }`}
        style={{ transform: 'translateZ(0)' }}
      >
        {/* Background Effects - Static for performance */}
        <div className="absolute inset-0 bg-gradient-to-br from-background via-background to-background/95" style={{ transform: 'translateZ(0)' }} />
        
        {/* Static Grid Pattern */}
        <div 
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: `
              linear-gradient(to right, currentColor 1px, transparent 1px),
              linear-gradient(to bottom, currentColor 1px, transparent 1px)
            `,
            backgroundSize: '50px 50px',
            transform: 'translateZ(0)',
            willChange: 'auto',
          }}
        />
        
        {/* Reduced Glowing Orbs - Only 2 for better performance */}
        <div 
          className="orb-glow absolute top-1/4 right-1/4 w-96 h-96 bg-[#19DCF5]/8 rounded-full blur-[100px] pointer-events-none" 
          style={{ animationDelay: '0s' }}
        />
        <div 
          className="orb-glow absolute bottom-1/4 left-1/4 w-96 h-96 bg-primary/8 rounded-full blur-[100px] pointer-events-none" 
          style={{ animationDelay: '1.5s' }}
        />
        
        {/* Main Content */}
        <div className="relative z-10 flex flex-col items-center justify-center" style={{ transform: 'translateZ(0)' }}>
          {/* Circular Progress with Logo */}
          <div className="relative mb-8">
            {/* Pulsing Rings - Behind the progress ring */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div 
                className="ring-expand w-48 h-48 md:w-56 md:h-56 border-2 border-[#19DCF5]/20 rounded-full"
                style={{ animationDelay: '0s' }}
              />
            </div>
            <div className="absolute inset-0 flex items-center justify-center">
              <div 
                className="ring-expand w-48 h-48 md:w-56 md:h-56 border border-[#19DCF5]/15 rounded-full"
                style={{ animationDelay: '1s' }}
              />
            </div>
            
            {/* Circular Progress Ring */}
            <svg 
              className="progress-ring w-48 h-48 md:w-56 md:h-56 relative z-10" 
              viewBox="0 0 120 120"
              style={{ transform: 'translateZ(0)' }}
            >
              {/* Background Circle */}
              <circle
                cx="60"
                cy="60"
                r="54"
                fill="none"
                stroke="currentColor"
                strokeWidth="4"
                className="text-border/20"
                style={{ transform: 'translateZ(0)' }}
              />
              {/* Progress Circle */}
              <circle
                cx="60"
                cy="60"
                r="54"
                fill="none"
                stroke="url(#progressGradient)"
                strokeWidth="4"
                strokeLinecap="round"
                className="progress-ring-circle"
                strokeDasharray={`${2 * Math.PI * 54}`}
                strokeDashoffset={`${2 * Math.PI * 54 * (1 - progress / 100)}`}
                style={{ transform: 'translateZ(0)' }}
              />
              {/* Gradient Definition */}
              <defs>
                <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#19DCF5" />
                  <stop offset="100%" stopColor="hsl(var(--primary))" />
                </linearGradient>
              </defs>
            </svg>
            
            {/* Logo and Percentage in Center */}
            <div className="absolute inset-0 flex flex-col items-center justify-center z-20">
              <div className="logo-float w-20 h-20 md:w-24 md:h-24 bg-gradient-to-br from-[#19DCF5]/20 to-primary/20 border-2 border-[#19DCF5]/30 rounded-2xl flex items-center justify-center shadow-2xl shadow-[#19DCF5]/20 mb-2">
                <img 
                  src={WebIcon} 
                  alt="SafeSurf Logo" 
                  className="w-12 h-12 md:w-16 md:h-16 rounded-full object-cover"
                  style={{ transform: 'translateZ(0)' }}
                  loading="eager"
                />
              </div>
              {/* Percentage Text */}
              <div className="text-center">
                <span className="text-2xl md:text-3xl font-bold text-[#19DCF5] tabular-nums" style={{ transform: 'translateZ(0)' }}>
                  {progress}%
                </span>
              </div>
            </div>
          </div>

          {/* Loading Text */}
          <div className="text-center" style={{ transform: 'translateZ(0)' }}>
            <h2 className="text-2xl md:text-3xl font-bold text-foreground mb-2 tracking-tight">
              SafeSurf AI
            </h2>
            <div className="w-24 h-1 bg-gradient-to-r from-transparent via-[#19DCF5] to-transparent mx-auto mb-4" />
            
            {/* Loading Dots Animation */}
            <div className="flex items-center justify-center gap-2">
              <div 
                className="dot-animate w-2 h-2 bg-[#19DCF5] rounded-full" 
                style={{ animationDelay: '0s' }}
              />
              <div 
                className="dot-animate w-2 h-2 bg-[#19DCF5] rounded-full" 
                style={{ animationDelay: '0.2s' }}
              />
              <div 
                className="dot-animate w-2 h-2 bg-[#19DCF5] rounded-full" 
                style={{ animationDelay: '0.4s' }}
              />
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default LoadingScreen;

