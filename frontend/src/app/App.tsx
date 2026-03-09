import { RouterProvider } from "react-router-dom";
import { appRouter } from "./routes";

export default function App() {
  return <RouterProvider router={appRouter} />;
}
