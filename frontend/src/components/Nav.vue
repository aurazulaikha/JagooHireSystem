<template>
  <nav class="navbar navbar-expand-lg navbar-absolute fixed-top navbar-transparent">
    <div class="container-fluid">
      <div class="navbar-wrapper">
        <div class="navbar-toggle">
          <button type="button" class="navbar-toggler">
            <span class="navbar-toggler-bar bar1"></span>
            <span class="navbar-toggler-bar bar2"></span>
            <span class="navbar-toggler-bar bar3"></span>
          </button>
        </div>
        <a class="navbar-brand" href="javascript:;">JAGOOHIRE</a>
      </div>

      <button
        class="navbar-toggler"
        type="button"
        data-toggle="collapse"
        data-target="#navigation"
        aria-controls="navigation-index"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-bar navbar-kebab"></span>
        <span class="navbar-toggler-bar navbar-kebab"></span>
        <span class="navbar-toggler-bar navbar-kebab"></span>
      </button>

      <div class="collapse navbar-collapse justify-content-end" id="navigation">
        <ul class="navbar-nav">
          <!-- Jika sudah login -->
          <li class="nav-item" v-if="isLoggedIn">
            <a class="logout-btn" href="javascript:;" @click="logout">
              <i class="nc-icon nc-button-power"></i>
            </a>
          </li>

          <!-- Jika belum login -->
          <li class="nav-item" v-else>
            <a class="login-btn" href="javascript:;" @click="goToLogin">
              <i class="nc-icon nc-single-02"></i>
            </a>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
import Swal from "sweetalert2";

export default {
  name: "NavBar",
  computed: {
    isLoggedIn() {
      return !!localStorage.getItem("user"); 
    },
  },
  methods: {
  async logout() {
    Swal.fire({
      title: "Konfirmasi Logout",
      text: "Apakah Anda yakin ingin keluar?",
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#d33",
      cancelButtonColor: "#946e6e",
      confirmButtonText: "Ya, Logout",
      cancelButtonText: "Batal",
    }).then(async (result) => {
      if (result.isConfirmed) {
        const user = JSON.parse(localStorage.getItem("user"));
        const token = user?.token;

        try {
          const response = await fetch("http://localhost:5000/logout", {
            method: "POST",
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/json",
            },
            credentials: "include",
          });

          if (response.ok) {
            Swal.fire({
              title: "Berhasil Logout!",
              text: "Anda telah keluar dari sistem.",
              icon: "success",
              confirmButtonColor: "#3085d6",
            });
          } else {
            console.warn("Logout gagal:", await response.text());
          }
        } catch (err) {
          console.error("Logout request error:", err);
        } finally {
          localStorage.removeItem("user");
          this.$router.push("/");
        }
      }
    });
  },
  goToLogin() {
    this.$router.push("/");
  },
}

};
</script>

<style>
.logout-btn,
.login-btn {
  background-color: #a26060;
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
}

.logout-btn i {
  color: white !important;
}

.login-btn {
  background-color: #ffffff;
}

.logout-btn:hover,
.login-btn:hover {
  opacity: 0.9;
  text-decoration: none;
}

.custom-logout-confirm-btn {
  background-color: #d33 !important;
  border-radius: 6px;
  color: #fff !important;
}

.custom-logout-cancel-btn {
  background-color: #946e6e !important;
  border-radius: 6px;
  color: #fff !important;
}

/* ukuran popup lebih normal */
.swal2-popup {
  font-size: 14px !important;
  padding: 20px !important;
}

.swal2-title {
  font-size: 16px !important;
}

.swal2-content {
  font-size: 14px !important;
}
</style>
