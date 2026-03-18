import Header from "@/components/Header";
import Hero from "@/components/Hero";
import URLChecker from "@/components/URLChecker";
import ModelPerformance from "@/components/ModelPerformance";
import HowItWorks from "@/components/HowItWorks";
import Features from "@/components/Features";
import About from "@/components/About";
import Footer from "@/components/Footer";

const Index = () => {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main>
        <Hero />
        <URLChecker />
        <ModelPerformance />
        <HowItWorks />
        <Features />
        <About />
      </main>
      <Footer />
    </div>
  );
};

export default Index;
