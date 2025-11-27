<template>
  <div class="edit-wrapper">
    <div class="edit-container">
      <h1 class="page-title">Edit Kandidat Request</h1>
      <div class="title-underline"></div>

      <form @submit.prevent="updateData">

        <!-- PILIH REQUEST -->
        <div class="form-group">
          <label>Pilih Request</label>
          <select v-model="form.request_id">
            <option disabled value="">-- pilih request --</option>
            <option
              v-for="req in requests"
              :key="req.id"
              :value="String(req.id)"
            >
              {{ req.id }} - {{ req.role }} ({{ req.company_name }})
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
              :value="String(cand.id)"
            >
              {{ cand.id }} - {{ cand.name }} ({{ cand.applied_role }})
            </option>
          </select>
        </div>

        <!-- ACTION BUTTON -->
        <div class="form-actions">
          <button type="submit" class="btn-save">Simpan Perubahan</button>
          <button type="button" class="btn-cancel" @click="goBack">Batal</button>
        </div>
      </form>

      <!-- ALERT -->
      <div v-if="showAlert" :class="['alert-box', alertType]">
        <p>{{ alertMessage }}</p>
        <button @click="closeAlert">OK</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "EditRequestCandidate",

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
      showAlert: false,
      alertMessage: "",
      alertType: "success",
    };
  },

  mounted() {
    this.fetchRequests();
    this.fetchCandidates();
    this.fetchDetail();
  },

  methods: {
    async fetchRequests() {
      try {
        const res = await axios.get("http://localhost:5000/requests", {
          headers: { Authorization: `Bearer ${this.token}` },
        });
        this.requests = res.data || [];
      } catch (error) {
        this.showAlertBox("Gagal mengambil data requests", "error");
      }
    },

    async fetchCandidates() {
      try {
        const res = await axios.get("http://localhost:5000/candidates", {
          headers: { Authorization: `Bearer ${this.token}` },
        });
        this.candidates = res.data || [];
      } catch (error) {
        this.showAlertBox("Gagal mengambil data kandidat", "error");
      }
    },

    async fetchDetail() {
      try {
        const id = this.$route.params.id;
        const res = await axios.get(
          `http://localhost:5000/request_candidates/${id}`,
          {
            headers: { Authorization: `Bearer ${this.token}` },
          }
        );

        const d = res.data;

        // String → select bind → convert Number saat submit
        this.form.request_id = String(d.request_id);
        this.form.candidate_id = String(d.candidate_id);
      } catch (error) {
        this.showAlertBox("Gagal mengambil data detail", "error");
      }
    },

    async updateData() {
      try {
        const id = this.$route.params.id;

        const payload = {
          request_id: Number(this.form.request_id),
          candidate_id: Number(this.form.candidate_id),
        };

        // Validation
        if (!payload.request_id || !payload.candidate_id) {
          this.showAlertBox("Request dan Kandidat wajib dipilih!", "error");
          return;
        }

        await axios.put(
          `http://localhost:5000/request_candidates/${id}`,
          payload,
          {
            headers: {
              Authorization: `Bearer ${this.token}`,
              "Content-Type": "application/json",
            },
          }
        );

        this.showAlertBox("Data berhasil diperbarui!", "success");

        setTimeout(() => this.$router.push("/requests"), 1500);
      } catch (error) {
        const msg = error.response?.data?.error || "Gagal memperbarui data!";
        this.showAlertBox(msg, "error");
      }
    },

    goBack() {
      this.$router.push("/requests");
    },

    showAlertBox(msg, type) {
      this.alertMessage = msg;
      this.alertType = type;
      this.showAlert = true;
    },

    closeAlert() {
      this.showAlert = false;
      if (this.alertType === "success") {
        this.goBack();
      }
    },
  },
};
</script>

<style scoped>
.edit-wrapper {
  display: flex;
  justify-content: flex-start;
  padding: 100px 0 0 50px;
  min-height: 100vh;
  background: linear-gradient(180deg, #f9f3f3, #fff);
}

.edit-container {
  width: 500px;
  background: #fff;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-title {
  font-size: 28px;
  color: #7a3e3e;
  font-weight: 700;
  margin-bottom: 5px;
}
.title-underline {
  width: 80px;
  height: 4px;
  background: #a26060;
  border-radius: 5px;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 20px;
}
.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #555;
}
.form-group select {
  width: 100%;
  padding: 10px 12px;
  border-radius: 6px;
  border: 1px solid #ddd;
  font-size: 14px;
  transition: border-color 0.3s;
}
.form-group select:focus {
  outline: none;
  border-color: #a26060;
}

.form-actions {
  margin-top: 25px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
.form-actions button {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.3s;
}
.btn-save {
  background: #43a032;
  color: white;
}
.btn-save:hover {
  background: #368825;
}
.btn-cancel {
  background: #6c757d;
  color: white;
}
.btn-cancel:hover {
  background: #5a6268;
}

.alert-box {
  margin-top: 20px;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
  font-weight: 500;
  border: 1px solid;
}
.alert-box.success {
  background: #d1e7dd;
  color: #0f5132;
  border-color: #badbcc;
}
.alert-box.error {
  background: #f8d7da;
  color: #842029;
  border-color: #f5c2c7;
}
.alert-box button {
  margin-top: 10px;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  background: #333;
  color: #fff;
  font-weight: 500;
}
.alert-box button:hover {
  background: #555;
}
</style>
