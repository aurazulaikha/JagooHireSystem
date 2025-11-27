<template>
  <div class="sidebar-wrapper">
    <ul class="nav">
      
      <li v-if="user && (user.role === 'HCM' || user.role === 'AM'|| user.role === 'Director')">
        <router-link to="/dashboard" active-class="active">
          <i class="nc-icon nc-chart-bar-32"></i>
          <p>Dashboard</p>
        </router-link>
      </li>

      <!-- Requests -->
      <li v-if="user && (user.role === 'HCM' || user.role === 'AM' || user.role === 'Director')">
        <router-link to="/requests" active-class="active">
          <i class="nc-icon nc-bullet-list-67"></i>
          <p>Requests</p>
        </router-link>
      </li>

      <!-- Candidates -->
      <li v-if="user && (user.role === 'HCM' || user.role === 'AM' || user.role === 'Director')">
        <router-link to="/candidates" active-class="active">
          <i class="nc-icon nc-single-copy-04"></i>
          <p>Candidates</p>
        </router-link>
      </li>

      <!-- Tests -->
      <li v-if="user && user.role === 'HCM'">
        <router-link to="/aptitude-tests" active-class="active">
          <i class="nc-icon nc-paper"></i>
          <p>Aptitude Tests</p>
        </router-link>
      </li>

      <li v-if="user && user.role === 'AM'">
        <router-link to="/technical-tests" active-class="active">
          <i class="nc-icon nc-badge"></i>
          <p>Technical Tests</p>
        </router-link>
      </li>

      <li v-if="user && user.role === 'Director'">
        <router-link to="/professional-tests" active-class="active">
          <i class="nc-icon nc-trophy"></i>
          <p>Professional Tests</p>
        </router-link>
      </li>

      <!-- Feedback (Director only) -->
      <li v-if="user && user.role === 'Director'">
        <router-link to="/feedbacks" active-class="active">
          <i class="nc-icon nc-check-2"></i>
          <p>Feedbacks</p>
        </router-link>
      </li>

      <!-- Users (HCM only) -->
      <li v-if="user && user.role === 'HCM'">
        <router-link to="/users" active-class="active">
          <i class="nc-icon nc-circle-10"></i>
          <p>Manage Users</p>
        </router-link>
      </li>

      <!-- Audit Logs (HCM only) -->
      <li v-if="user && user.role === 'HCM'">
        <router-link to="/audit-logs" active-class="active">
          <i class="nc-icon nc-tile-56"></i>
          <p>Audit Logs</p>
        </router-link>
      </li>

      <!-- Profile / Logout (Semua user) -->
      <li v-if="user">
        <router-link to="/profile" active-class="active">
          <i class="nc-icon nc-single-02"></i>
          <p>Profil</p>
        </router-link>
      </li>
    </ul>

    <!-- Popup login -->
    <div v-if="showLoginPopup" class="popup-overlay">
      <div class="popup-box">
        <p style="font-size: 1.3rem">
          Login untuk mengakses {{ targetPage }}
        </p>
        <div class="popup-actions">
          <button class="btn btn-success" @click="goToLogin">Login</button>
          <button class="btn btn-secondary" @click="showLoginPopup = false">
            Batal
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "SidebarPage",
  data() {
    return {
      showLoginPopup: false,
      targetPage: "",
      user: null,
    };
  },
  created() {
    const storedUser = localStorage.getItem("user");
    this.user = storedUser ? JSON.parse(storedUser) : null;
  },
  methods: {
    isLoggedIn() {
      return !!localStorage.getItem("user");
    },
    handleProtectedNav(page) {
      if (this.isLoggedIn()) {
        this.$router.push("/" + page);
      } else {
        this.targetPage = page;
        this.showLoginPopup = true;
      }
    },
    goToLogin() {
      this.showLoginPopup = false;
      this.$router.push("/login");
    },
  },
};
</script>

<style scoped>
.nav li a {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 15px;
  color: #333;
  text-decoration: none;
  border-radius: 10px;
  transition: 0.3s;
  font-weight: bold;
}

.nav li a:hover {
  background-color: #9d5656 !important;
  color: white !important;
}

.nav li a:hover i {
  color: white !important;
  font-weight: bold;
}

.nav li a.active {
  background-color: #9d5656 !important;
  color: white !important;
  font-weight: bold;
}

.nav li a.active i,
.nav li a.active p {
  color: white !important;
  font-weight: bold;
}

.popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.popup-box {
  background: white;
  padding: 20px 30px;
  border-radius: 12px;
  text-align: center;
}

.popup-actions button {
  margin: 5px;
}
</style>
