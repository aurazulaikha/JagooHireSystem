import { createRouter, createWebHistory } from 'vue-router'
import Login from '@/views/Login.vue'
import Dashboard from '@/views/Dashboard.vue';
import Candidate from '@/views/Candidate.vue';
import AddCandidate from '@/views/AddCandidate.vue';
import EditCandidate from '@/views/EditCandidate.vue';
import Request from '@/views/Request.vue';
import AddRequest from '@/views/AddRequest.vue';
import EditRequest from '@/views/EditRequest.vue';
import AptitudeTest from '@/views/AptitudeTest.vue';
import AptitudeTestForm from '@/views/AptitudeTestForm.vue';
import TechnicalTest from '@/views/TechnicalTest.vue';
import TechnicalTestForm from '@/views/TechnicalTestForm.vue';
import ManageUsers from '@/views/ManageUsers.vue';
import AddUser from '@/views/AddUser.vue';
import EditUsers from '@/views/EditUsers.vue';
import AuditLogs from '@/views/AuditLogs.vue';
import UserProfile from '@/views/UserProfile.vue';
import EditProfilePage from '@/views/EditProfilePage.vue';


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
  {
    path: '/aptitude-tests',
    name: 'AptitudeTest',
    component: AptitudeTest,
    meta: { requiresAuth: true, role: ['HCM']}
  },
  {
    path: '/aptitude-test/penilaian',
    name: 'AptitudeTestForm',
    component: AptitudeTestForm,
    meta: { requiresAuth: true, role: ['HCM']}
  },
  {
    path: '/technical-tests',
    name: 'TechnicalTest',
    component: TechnicalTest,
    meta: { requiresAuth: true, role: ['AM']}
  },
  {
    path: '/technical-test/penilaian',
    name: 'TechnicalTestForm',
    component: TechnicalTestForm,
    meta: { requiresAuth: true, role: ['AM']}
  },
  {
    path: '/users',
    name: 'ManageUsers',
    component: ManageUsers,
    meta: { requiresAuth: true, role: ['HCM']}
  },
  {
    path: '/add-user',
    name: 'AddUser',
    component: AddUser,
    meta: { requiresAuth: true, role: 'HCM'}
  },
  {
    path: '/edit-user/:id',
    name: 'EditUsers',
    component: EditUsers,
    meta: { requiresAuth: true, role: 'HCM'}
  },
    {
    path: '/audit-logs',
    name: 'AuditLogs',
    component: AuditLogs,
    meta: { requiresAuth: true, role: ['HCM'] }
  },
  {
    path: '/profile',
    name: 'UserProfile',
    component: UserProfile,
    meta: { requiresAuth: true, role: ['HCM','AM','Director']}
  },
    {
    path: '/profile/edit',
    name: 'EditProfilePage',
    component: EditProfilePage,
    meta: { requiresAuth: true, role: ['HCM', 'AM', 'Director'] }
  },

]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router