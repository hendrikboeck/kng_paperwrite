import { EuiProvider } from '@elastic/eui';
import { HashRouter as Router, Routes, Route } from 'react-router-dom';
import CreateNewPage from './CreateNewPage.jsx'
import OverviewPage from './OverviewPage.jsx';
import DetailsPage from './DetailsPage.jsx';

//import '@elastic/eui/dist/eui_theme_light.css';
import '@elastic/eui/dist/eui_theme_dark.css';

const App = () => {
  return (
    <Router>
      <EuiProvider colorMode="dark">


        <Routes>

          <Route
            path="/create_new"
            element={<CreateNewPage />}
          />

          <Route
            path="/details"
            element={<DetailsPage />}
          />

          <Route
            path="/"
            element={<OverviewPage />}
          />

        </Routes>

      </EuiProvider>
    </Router>
  );
};

export default App;
