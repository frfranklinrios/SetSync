import Admin from "./Admin.jsx";
import Storefront from "./Storefront.jsx";

export default function App() {
  if (window.location.pathname.startsWith("/admin")) {
    return <Admin />;
  }
  return <Storefront />;
}
