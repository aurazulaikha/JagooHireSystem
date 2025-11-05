import { createRouter, createWebHistory } from 'vue-router'
import Login from '@/views/Login.vue'
import Dashboard from '@/views/Dashboard.vue';
import Candidate from '@/views/Candidate.vue';
import AddCandidate from '@/views/AddCandidate.vue';
import EditCandidate from '@/views/EditCandidate.vue';
import Request from '@/views/Request.vue';
import AddRequest from '@/views/AddRequest.vue';
import EditRequest from '@/views/EditRequest.vue';


const routes = [
  {
    path: '/',
    name: 'Login',
    component: Login,
    meta: { noNavbar: true, noSidebar: true, noFooter: true }
  },
  {
    path: '/dashboard',
    name: 'DashboardPage',
    component: Dashboard,
    meta: { requiresAuth: true, role: ['HCM','AM','Director']}
  },
  {
    path: '/candidates',
    name: 'CandidatesPage',
    component: Candidate,
    meta: { requiresAuth: true, role: ['HCM','AM','Director']}
  },
  {
    path: '/add-candidate',
    name: 'AddCandidate',
    component: AddCandidate,
    meta: { requiresAuth: true, role: 'HCM'}
  },
  {
    path: '/edit-candidate/:id',
    name: 'EditCandidate',
    component: EditCandidate,
    meta: { requiresAuth: true, role: 'HCM'}
  },
  {
    path: '/requests',
    name: 'RequestsPage',
    component: Request,
    meta: { requiresAuth: true, role: ['HCM','AM','Director']}
  },
  {
    path: '/add-request',
    name: 'AddRequest',
    component: AddRequest,
    meta: { requiresAuth: true, role: 'AM'}
  },
  {
    path: '/edit-request/:id',
    name: 'EditRequest',
    component: EditRequest,
    meta: { requiresAuth: true, role: 'AM'}
  },

]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router