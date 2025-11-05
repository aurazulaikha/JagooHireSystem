<template>
  <div class="edit-wrapper">
    <div class="edit-container">
      <div class="header">
        <h1>Edit Profil</h1>
        <div class="underline"></div>
      </div>

      <div class="card">
        <form @submit.prevent="updateProfile">
          <div class="form-group">
            <label>Nama Lengkap</label>
            <input v-model="form.username" type="text" placeholder="Masukkan nama Anda" required />
          </div>

          <div class="form-group">
            <label>Email</label>
            <input v-model="form.email" type="email" placeholder="Masukkan email Anda" required />
          </div>

          <div class="form-group">
            <label>Telepon</label>
            <input v-model="form.telp" type="text" placeholder="Masukkan nomor telepon" />
          </div>

          <div class="btn-group">
            <router-link to="/profile" class="btn btn-cancel">Batal</router-link>
            <button type="submit" class="btn btn-save">Simpan</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "EditProfile",
  data() {
    return {
      form: {
        username: "",
        email: "",
        telp: "",
      },
    };
  },
  mounted() {
    this.loadProfile();
  },
  methods: {
    async loadProfile() {
      try {
        const token = JSON.parse(localStorage.getItem("user"))?.token;
        const res = await fetch("http://localhost:5000/profile", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) throw new Error("Gagal memuat profil");
        const data = await res.json();
        this.form = { username: data.username, email: data.email, telp: data.telp };
      } catch (err) {
        alert("Gagal memuat data profil: " + err.message);
      }
    },
    async updateProfile() {
      try {
        const token = JSON.parse(localStorage.getItem("user"))?.token;
        const res = await fetch("http://localhost:5000/profile", {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(this.form),
        });

        if (res.ok) {
          alert("Profil berhasil diperbarui!");
          this.$router.push("/profile");
        } else {
          const errData = await res.json().catch(() => ({}));
          alert("Gagal memperbarui profil: " + (errData.message || "Terjadi kesalahan."));
        }
      } catch (err) {
        alert("Gagal terhubung ke server: " + err.message);
      }
    },
  },
};
</script>

<style scoped>
.edit-wrapper {
  background: linear-gradient(180deg, #f9f3f3, #fff);
  min-height: 100vh;
  display: flex;
  justify-content: center;
  padding: 90px 0;
  font-family: "Poppins", sans-serif;
}

.edit-container {
  width: 90%;
  max-width: 600px;
}

.header h1 {
  color: #7a3e3e;
  font-size: 30px;
  font-weight: 700;
  margin-bottom: 8px;
}

.underline {
  width: 80px;
  height: 4px;
  background: #a26060;
  border-radius: 4px;
  margin-bottom: 20px;
}

.card {
  background: #fff;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 6px 16px rgba(162, 96, 96, 0.15);
  border: 1px solid #f1e4e4;
}

.form-group {
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
}

label {
  font-weight: 600;
  margin-bottom: 6px;
  color: #7a3e3e;
}

input {
  padding: 10px;
  border-radius: 10px;
  border: 1px solid #d8b6b6;
  outline: none;
  transition: border 0.3s;
}

input:focus {
  border-color: #a26060;
}

.btn-group {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 25px;
}

.btn {
  padding: 10px 20px;
  border-radius: 10px;
  font-weight: 600;
  text-decoration: none;
  transition: 0.3s;
}

.btn-save {
  background: #a26060;
  color: #fff;
}

.btn-save:hover {
  background: #7a3e3e;
}

.btn-cancel {
  background: #ccc;
  color: #333;
}

.btn-cancel:hover {
  background: #aaa;
}
</style>
