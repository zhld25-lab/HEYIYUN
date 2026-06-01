import React from 'react';
import { RouterProvider } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ConfigProvider, App as AntApp } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import { router } from '@/router';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, refetchOnWindowFocus: false },
  },
});

const theme = {
  token: {
    colorPrimary: '#1d4ed8',
    borderRadius: 4,
  },
};

const App: React.FC = () => (
  <ConfigProvider locale={zhCN} theme={theme}>
    <AntApp>
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
      </QueryClientProvider>
    </AntApp>
  </ConfigProvider>
);

export default App;
