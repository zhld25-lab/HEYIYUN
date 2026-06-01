import React from 'react';
import { createBrowserRouter, Navigate } from 'react-router-dom';
import BasicLayout from '@/layouts/BasicLayout';
import AuthLayout from '@/layouts/AuthLayout';
import Login from '@/pages/Login';
import Dashboard from '@/pages/Dashboard';
import HomeWorkbench from '@/pages/HomeWorkbench';
import ProjectList from '@/pages/ProjectCenter/ProjectList';
import ProjectForm from '@/pages/ProjectCenter/ProjectForm';
import ProjectDetail from '@/pages/ProjectCenter/ProjectDetail';
import SystemSettings from '@/pages/SystemSettings';

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <AuthLayout />,
    children: [{ index: true, element: <Login /> }],
  },
  {
    path: '/',
    element: <BasicLayout />,
    children: [
      { index: true, element: <Navigate to="/dashboard" replace /> },
      { path: 'home', element: <HomeWorkbench /> },
      { path: 'dashboard', element: <Dashboard /> },
      { path: 'projects', element: <ProjectList /> },
      { path: 'projects/create', element: <ProjectForm /> },
      { path: 'projects/:id', element: <ProjectDetail /> },
      { path: 'projects/:id/edit', element: <ProjectForm /> },
      { path: 'system', element: <SystemSettings /> },
    ],
  },
  { path: '*', element: <Navigate to="/dashboard" replace /> },
]);
