import axios from 'axios';
const api = axios.create({ baseURL: 'http://localhost:8000' });

export const getIssues      = () => api.get('/api/issues/summary');
export const getPRs         = () => api.get('/api/prs/summary');
export const getCI          = () => api.get('/api/ci/stability');
export const getReleases    = () => api.get('/api/releases/pr-velocity');
export const getContributors= () => api.get('/api/contributors/ranking');
export const getBusFactor   = () => api.get('/api/contributors/bus-factor');
