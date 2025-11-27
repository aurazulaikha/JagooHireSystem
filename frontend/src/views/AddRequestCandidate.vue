<template>
  <div class="form-wrapper">
    <div class="form-container">
      <h1>Tambah Kandidat Request</h1>

      <!-- PILIH REQUEST -->
      <div class="form-group">
        <label>Pilih Request</label>
        <select v-model="form.request_id">
          <option disabled value="">-- pilih request --</option>
          <option
            v-for="req in requests"
            :key="req.id"
            :value="req.id"
          >
            {{ req.company_name }} - {{ req.role }}
          </option>
        </select>
      </div>

      <!-- PILIH KANDIDAT -->
      <div class="form-group">
        <label>Pilih Kandidat</label>
        <select v-model="form.candidate_id">
          <option disabled value="">-- pilih kandidat --</option>
          <option
            v-for="cand in candidates"
            :key="cand.id"
            :value="cand.id"
          >
            {{ cand.name }} ({{ cand.applied_role }})
          </option>
        </select>
      </div>

      <div class="form-actions">
        <button class="btn-save" @click="submitForm" :disabled="loading">
          {{ loading ? 'Menyimpan...' : 'Simpan' }}
        </button>
        <button class="btn-cancel" @click="$router.push('/requests')">Batal</button>
      </div>
    </div>

    <!-- Popup Error -->
    <div v-if="showErrorPopup" class="popup-overlay">
      <div class="popup-container">
        <div class="popup-header">
          <h3>⚠️ Tidak Dapat Menambahkan Kandidat</h3>
        </div>
        <div class="popup-body">
          <p>{{ errorMessage }}</p>
        </div>
        <div class="popup-footer">
          <button class="btn-ok" @click="closeErrorPopup">Mengerti</button>
        </div>
      </div>
    </div>

    <!-- Popup Success -->
    <div v-if="showSuccessPopup" class="popup-overlay">
      <div class="popup-container success-popup">
        <div class="popup-header">
          <h3>✅ Berhasil</h3>
        </div>
        <div class="popup-body">
          <p>Kandidat berhasil ditambahkan ke request!</p>
        </div>
        <div class="popup-footer">
          <button class="btn-ok" @click="closeSuccessPopup">OK</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "AddRequestCandidate",
  data() {
    const user = JSON.parse(localStorage.getItem("user")) || {};
    return {
      token: user.token || "",
      form: {
        request_id: "",
        candidate_id: "",
      },
      requests: [],
      candidates: [],
      loading: false,
      showErrorPopup: false,
      showSuccessPopup: false,
      errorMessage: ""
    };
  },

  mounted() {
    this.loadData();
  },

  methods: {
    async loadData() {
      try {
        const [reqRes, candRes] = await Promise.all([
          axios.get("http://localhost:5000/requests", {
            headers: { Authorization: `Bearer ${this.token}` },
          }),
          axios.get("http://localhost:5000/candidates", {
            headers: { Authorization: `Bearer ${this.token}` },
          }),
        ]);

        this.requests = reqRes.data;
        this.candidates = candRes.data;
      } catch (error) {
        this.showError("Gagal memuat data: " + (error.response?.data?.message || error.message));
      }
    },

    async submitForm() {
      if (!this.form.request_id || !this.form.candidate_id) {
        this.showError("Pilih request dan kandidat terlebih dahulu!");
        return;
      }

      this.loading = true;

      try {
        await axios.post("http://localhost:5000/request_candidates", this.form, {
          headers: { Authorization: `Bearer ${this.token}` },
        });

        this.showSuccessPopup = true;
        
      } catch (error) {
        if (error.response?.status === 409) {
          this.showError("Kandidat ini sudah dipasangkan dengan request tersebut sebelumnya. Silakan pilih kandidat atau request lainnya.");
        } else {
          this.showError("Terjadi kesalahan: " + (error.response?.data?.message || error.message));
        }
      } finally {
        this.loading = false;
      }
    },

    showError(message) {
      this.errorMessage = message;
      this.showErrorPopup = true;
    },

    closeErrorPopup() {
      this.showErrorPopup = false;
      this.errorMessage = "";
    },

    closeSuccessPopup() {
      this.showSuccessPopup = false;
      this.$router.push("/requests");
    }
  },
};
</script>

<style scoped>
.form-wrapper {
  display: flex;
  justify-content: center;
  padding: 100px 0;
  position: relative;
}
.form-container {
  width: 400px;
  background: #fff;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.2);
}
h1 {
  text-align: center;
  color: #7a3e3e;
  margin-bottom: 20px;
}
.form-group {
  margin-bottom: 15px;
  display: flex;
  flex-direction: column;
}
label {
  font-weight: 600;
  margin-bottom: 6px;
}
select {
  padding: 8px;
  border-radius: 8px;
  border: 1px solid #ccc;
}
.form-actions {
  display: flex;
  justify-content: space-between;
}
.btn-save {
  background: #a26060;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
}
.btn-save:disabled {
  background: #ccc;
  cursor: not-allowed;
}
.btn-cancel {
  background: #ccc;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
}

/* Popup Styles */
.popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.popup-container {
  background: white;
  border-radius: 12px;
  width: 400px;
  max-width: 90%;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
  overflow: hidden;
}

.success-popup {
  border-top: 4px solid #4CAF50;
}

.popup-header {
  background: #f8f9fa;
  padding: 20px;
  border-bottom: 1px solid #dee2e6;
}

.popup-header h3 {
  margin: 0;
  color: #333;
}

.popup-body {
  padding: 20px;
}

.popup-body p {
  margin: 0;
  line-height: 1.5;
  color: #555;
}

.popup-footer {
  padding: 15px 20px;
  background: #f8f9fa;
  border-top: 1px solid #dee2e6;
  text-align: right;
}

.btn-ok {
  background: #a26060;
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.btn-ok:hover {
  background: #8a5252;
}
</style>