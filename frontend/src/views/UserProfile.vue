<template>
  <div class="profile-wrapper">
    <div class="profile-container">
      <!-- Header -->
      <div class="profile-header">
        <h1 class="profile-title">Profil Saya</h1>
        <div class="title-underline"></div>
      </div>

      <!-- Profile Card -->
      <div class="profile-card">
        <div class="profile-main">
          <div class="profile-avatar">
            {{ user?.username?.charAt(0).toUpperCase() }}
          </div>
          <div class="profile-info">
            <h2 class="profile-name">{{ user?.username }}</h2>
            <p class="profile-role">{{ user?.role }}</p>
          </div>
        </div>

        <div class="profile-details">
          <div class="detail-item">
            <p class="label">Email</p>
            <p class="value">{{ user?.email }}</p>
          </div>
          <div class="divider"></div>

          <div class="detail-item">
            <p class="label">Telepon</p>
            <p class="value">{{ user?.telp || '-' }}</p>
          </div>
          <div class="divider"></div>

          <div class="detail-item">
            <p class="label">Dibuat pada</p>
            <p class="value">{{ formatDate(user?.created_at) }}</p>
          </div>
        </div>

        <div class="profile-actions">
          <router-link to="/profile/edit" class="btn-action btn-edit">
            Edit Profil
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "UserProfile",
  data() {
    return { user: null };
  },
  mounted() {
    this.getProfile();
  },
  methods: {
    async getProfile() {
      try {
        const token = JSON.parse(localStorage.getItem("user"))?.token;
        const res = await fetch("http://localhost:5000/profile", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) throw new Error("Gagal mengambil profil");
        this.user = await res.json();
      } catch (err) {
        console.error("Gagal memuat profil:", err);
      }
    },
    formatDate(dateString) {
      if (!dateString) return "-";
      const date = new Date(dateString);
      return date.toLocaleDateString("id-ID", {
        day: "2-digit",
        month: "long",
        year: "numeric",
      });
    },
  },
};
</script>

<style scoped>
.profile-wrapper {
  background: linear-gradient(180deg, #f9f3f3, #fff);
  min-height: 100vh;
  display: flex;
  justify-content: center;
  padding: 90px 0;
  font-family: "Poppins", sans-serif;
}

.profile-container {
  width: 90%;
  max-width: 800px;
}

.profile-header {
  text-align: left;
  margin-bottom: 35px;
}

.profile-title {
  font-size: 30px;
  font-weight: 700;
  color: #7a3e3e;
  margin-bottom: 6px;
}

.title-underline {
  width: 80px;
  height: 3px;
  background: #a26060;
  border-radius: 4px;
}

/* === Card === */
.profile-card {
  background: #fff;
  border-radius: 14px;
  padding: 35px 28px;
  box-shadow: 0 5px 14px rgba(162, 96, 96, 0.12);
  border: 1px solid #f1e4e4;
  text-align: center;
}

.profile-main {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;
}

.profile-avatar {
  width: 95px;
  height: 95px;
  border-radius: 50%;
  background: #a26060;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 38px;
  font-weight: 700;
  box-shadow: 0 3px 6px rgba(162, 96, 96, 0.25);
  margin-bottom: 8px;
}

.profile-info h2 {
  font-size: 21px;
  font-weight: 700;
  color: #7a3e3e;
  margin-bottom: 3px;
}

.profile-role {
  color: #666;
  font-size: 13px;
}

/* === Detail === */
.profile-details {
  margin-top: 10px;
  text-align: left;
}

.detail-item {
  display: flex;
  flex-direction: column;
  margin: 3px 0;
}

.label {
  font-size: 13px;
  color: #777;
  line-height: 1.3;
}

.value {
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.divider {
  height: 0.5px;
  background: #ddd;
  margin: 4px 0 6px;
}

/* === Buttons === */
.profile-actions {
  display: flex;
  justify-content: center;
  margin-top: 25px;
}

.btn-action {
  padding: 11px 35px;
  border-radius: 10px;
  font-weight: 600;
  color: #fff;
  transition: 0.3s;
  text-decoration: none;
}

.btn-edit {
  background: #a26060;
}

.btn-edit:hover {
  background: #7a3e3e;
}
</style>
