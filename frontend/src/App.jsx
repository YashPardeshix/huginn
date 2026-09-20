import { BrowserRouter, Routes, Route } from "react-router-dom";
import NavBar from "./components/NavBar";
import Runs from "./pages/Runs";
import FixComparison from "./pages/FixComparison";
import Repositories from "./pages/Repositories";
import Metrics from "./pages/Metrics";
import Audit from "./pages/Audit";

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-background">
        <NavBar />
        <Routes>
          <Route path="/" element={<Runs />} />
          <Route path="/fix-comparison" element={<FixComparison />} />
          <Route path="/repositories" element={<Repositories />} />
          <Route path="/metrics" element={<Metrics />} />
          <Route path="/audit" element={<Audit />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
