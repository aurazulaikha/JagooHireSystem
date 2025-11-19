<template>
  <div class="dashboard-wrapper">
    <div class="dashboard-container">
      <!-- Dashboard Header -->
      <div class="dashboard-header">
        <h1 class="dashboard-title">Dashboard</h1>
        <div class="title-underline"></div>
      </div>

      <!-- Summary Cards -->
      <div class="summary-cards">
        <div class="card" v-for="(item, i) in summaryItems" :key="i">
          <div class="card-content">
            <div class="card-icon"><i :class="item.icon"></i></div>
            <div class="card-info">
              <h3>{{ item.title }}</h3>
              <p class="card-value">{{ item.value }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Active Requests -->
      <div class="section">
        <div class="section-header"><h2>Active Requests Overview</h2></div>

  
        
          <input
            type="text"
            v-model="searchRequests"
            class="requests-search"
            placeholder="Search requests..."
          />
      

        <table class="request-table">
          <thead>
            <tr>
              <th>Role</th>
              <th>Company</th>
              <th>Max Salary</th>
              <th>Qty Required</th>
              <th>Status (Onboarded/Total)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in paginatedRequests" :key="r.id">
              <td>{{ r.role }}</td>
              <td>{{ r.company_name || '—' }}</td>
              <td>{{ r.max_salary || '—' }}</td>
              <td>{{ r.quantity }}</td>
              <td>{{ rStatus(r.id) }}</td>
            </tr>
          </tbody>
        </table>

        <!-- pagination for requests if needed -->
        <div v-if="requestsTotalPages > 1" class="pagination" style="margin-top:12px;">
          <button @click="prevRequestsPage" :disabled="requestsPage === 1">Prev</button>
          <span>Page {{ requestsPage }} of {{ requestsTotalPages }}</span>
          <button @click="nextRequestsPage" :disabled="requestsPage === requestsTotalPages">Next</button>
        </div>
      </div>

      <!-- Today's Schedule -->
      <div class="section schedule-section">
        <h2>Today's Assessment Schedule</h2>
        <div v-if="todaysSchedule.length > 0" class="calendar-container">
          <div v-for="s in todaysSchedule" :key="s.request_candidate_id" class="calendar-card">
            <div class="calendar-date">
              <div class="calendar-day">{{ new Date(s.schedule_datetime).getDate() }}</div>
              <div class="calendar-month">
                {{ new Date(s.schedule_datetime).toLocaleString('default', { month: 'short' }) }}
              </div>
            </div>
            <div class="calendar-info">
              <h4 class="stage">{{ s.stage }}</h4>
              <p class="candidate-name"><i class="fa fa-user"></i> {{ s.candidate_name }}</p>
            </div>
          </div>
        </div>
        <p v-else class="no-schedule">No assessments scheduled for today.</p>
      </div>

      <!-- Test Phase Section -->
      <div class="section">
        <h2>Test Phases Data</h2>

        <!-- Phase Buttons + Search (phase-header) -->
        <div class="phase-header">
          <div class="phase-buttons">
            <button
              v-for="(phase, index) in ['Aptitude', 'Technical', 'Professional']"
              :key="index"
              @click="changePhase(phase)"
              :class="{ active: activePhase === phase }"
            >
              {{ phase }}
            </button>
          </div>

          <!-- Phase Search (global across all phases, FAST) -->
          <input
            type="text"
            v-model="searchPhase"
            class="phase-search"
            placeholder="Search phases..."
          />
        </div>

        <!-- Scrollable Table -->
        <div v-if="paginatedData.length" class="table-scroll-wrapper">
          <table class="request-table">
            <thead>
              <tr>
                <th>No</th>
                <th>Request Candidate ID</th>
                <th>Nama Kandidat</th>
                <th>Role Dilamar</th>
                <th>Role Dibutuhkan</th>
                <th>Email Kandidat</th>
                <th>HP/Telp</th>
                <th>Domisili</th>
                <th>Perusahaan</th>
                <th>Lokasi Kerja</th>
                <th>Metode Kerja</th>
                <th>Jadwal Kerja</th>
                <th>Level</th>
                <th>Tanggal Tes</th>
                <th v-for="key in dynamicColumnsFiltered" :key="key">
                  {{ readableColumnName(key) }}
                </th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="(row, i) in paginatedData" :key="i">
                <td>{{ (currentPage - 1) * itemsPerPage + i + 1 }}</td>
                <td>{{ row.request_candidate_id || '—' }}</td>
                <td>{{ row.candidate_name || '—' }}</td>
                <td>{{ row.applied_role || '—' }}</td>
                <td>{{ row.requested_role || '—' }}</td>

                <td>
                  <a v-if="row.candidate_email" :href="`mailto:${row.candidate_email}`">
                    {{ row.candidate_email }}
                  </a>
                  <span v-else>—</span>
                </td>

                <td>{{ row.no_telp || '—' }}</td>
                <td>{{ row.domisili || '—' }}</td>
                <td>{{ row.company_name || '—' }}</td>
                <td>{{ row.location || '—' }}</td>
                <td>{{ row.work_method || '—' }}</td>
                <td>{{ row.work_schedule || '—' }}</td>
                <td>{{ row.level || '—' }}</td>
                <td>{{ formatCellValue('test_date', row.test_date) }}</td>

                <!-- Dynamic phase-specific columns -->
                <td v-for="key in dynamicColumnsFiltered" :key="key">
                  <span v-if="getCellClass(key, row[key])" :class="['status-badge', getCellClass(key, row[key])]">
                    {{ formatCellValue(key, row[key]) }}
                  </span>
                  <span v-else>{{ formatCellValue(key, row[key]) }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination for phase table -->
        <div v-if="totalPages > 1" class="pagination">
          <button @click="prevPage" :disabled="currentPage === 1">Prev</button>
          <span>Page {{ currentPage }} of {{ totalPages }}</span>
          <button @click="nextPage" :disabled="currentPage === totalPages">Next</button>
        </div>

        <p v-else-if="!activePhaseData.length" class="no-schedule">
          No data available for this phase.
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "DashboardPage",
  data() {
    return {
      requests: [],
      candidates: [],
      todaysSchedule: [],
      dashboardData: {},
      activePhase: "Aptitude",
      currentPage: 1,
      itemsPerPage: 10,
      // pagination for requests table
      requestsPage: 1,
      requestsPerPage: 8,

      // search states
      searchRequests: "",
      searchPhase: ""
    };
  },

  computed: {
    summaryItems() {
      const onboarded = this.candidates.filter(c => c.status === "Onboarding").length;
      const avgConversion = this.candidates.length
        ? Math.round((onboarded / this.candidates.length) * 100)
        : 0;

      return [
        { title: "Active Requests", value: this.requests.length, icon: "fa fa-briefcase" },
        { title: "Total Candidates", value: this.candidates.length, icon: "fa fa-users" },
        { title: "Positions Filled", value: onboarded, icon: "fa fa-check-circle" },
        { title: "Avg Conversion", value: `${avgConversion}%`, icon: "fa fa-area-chart" },
      ];
    },

    // ---------------------
    // REQUESTS: frontend FAST filter (searchRequests)
    // ---------------------
    normalizedRequests() {
      // ensure default structure if API returns non-array
      return Array.isArray(this.requests) ? this.requests : [];
    },

    filteredRequests() {
      if (!this.searchRequests) return this.normalizedRequests;
      const q = this.searchRequests.toLowerCase();
      return this.normalizedRequests.filter(row =>
        Object.values(row).some(val =>
          val !== null && val !== undefined && String(val).toLowerCase().includes(q)
        )
      );
    },

    requestsTotalPages() {
      return Math.ceil(this.filteredRequests.length / this.requestsPerPage) || 1;
    },

    paginatedRequests() {
      const start = (this.requestsPage - 1) * this.requestsPerPage;
      return this.filteredRequests.slice(start, start + this.requestsPerPage);
    },

    // ---------------------
    // PHASES: original phase data (from dashboardData)
    // We'll create filtered versions based on searchPhase (global across phases)
    // ---------------------
    rawAptitude() {
      return this.dashboardData.aptitude_phase || [];
    },
    rawTechnical() {
      return this.dashboardData.technical_phase || [];
    },
    rawProfessional() {
      return this.dashboardData.professional_phase || [];
    },

    // helper: filtered arrays per-phase using searchPhase (case-insensitive)
    filteredAptitude() {
      return this._filterRowsByQuery(this.rawAptitude, this.searchPhase);
    },
    filteredTechnical() {
      return this._filterRowsByQuery(this.rawTechnical, this.searchPhase);
    },
    filteredProfessional() {
      return this._filterRowsByQuery(this.rawProfessional, this.searchPhase);
    },

    // activePhaseData returns filtered data for the currently active phase
    activePhaseData() {
      switch (this.activePhase) {
        case "Aptitude":
          return this.filteredAptitude;
        case "Technical":
          return this.filteredTechnical;
        case "Professional":
          return this.filteredProfessional;
        default:
          return [];
      }
    },

    // dynamicColumnsFiltered logic remains same: infer extra columns from activePhaseData
    filteredColumns() {
      if (!this.activePhaseData.length) return [];

      const hidden = [
        "id","aptitude_test_id","technical_test_id","professional_test_id",
        "candidate_id","rc_id","request_id",
        "applied_role","requested_role",
        "candidate_email","no_telp","domisili",
        "company_name","location","work_method","work_schedule","level","test_date",
        "request_candidate_id"
      ];

      return Object.keys(this.activePhaseData[0]).filter(
        key => !hidden.includes(key) && key !== "candidate_name"
      );
    },

    dynamicColumnsFiltered() {
      return this.filteredColumns;
    },

    totalPages() {
      return Math.ceil(this.activePhaseData.length / this.itemsPerPage) || 1;
    },

    paginatedData() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      return this.activePhaseData.slice(start, start + this.itemsPerPage);
    }
  },

  async created() {
    const user = JSON.parse(localStorage.getItem("user"));
    const token = user?.token;
    const headers = { Authorization: `Bearer ${token}` };

    try {
      const dashboardRes = await axios.get("http://localhost:5000/dashboard", { headers });
      this.dashboardData = dashboardRes.data;

      const [reqRes, candRes] = await Promise.all([
        axios.get("http://localhost:5000/requests", { headers }),
        axios.get("http://localhost:5000/candidates", { headers }),
      ]);

      this.requests = reqRes.data;
      this.candidates = candRes.data;

      this.todaysSchedule = this.dashboardData.todays_schedule || [];
    } catch (e) {
      console.error(e);
    }
  },

  methods: {
    // ---------------------
    // Paging controls for phases
    // ---------------------
    changePhase(phase) {
      this.activePhase = phase;
      this.currentPage = 1;
    },
    nextPage() {
      if (this.currentPage < this.totalPages) this.currentPage++;
    },
    prevPage() {
      if (this.currentPage > 1) this.currentPage--;
    },

    // ---------------------
    // Paging controls for requests
    // ---------------------
    nextRequestsPage() {
      if (this.requestsPage < this.requestsTotalPages) this.requestsPage++;
    },
    prevRequestsPage() {
      if (this.requestsPage > 1) this.requestsPage--;
    },

    _filterRowsByQuery(rows, query) {
      if (!Array.isArray(rows)) return [];
      if (!query) return rows;
      const q = String(query).toLowerCase();
      return rows.filter(row =>
        Object.values(row).some(val =>
          val !== null && val !== undefined && String(val).toLowerCase().includes(q)
        )
      );
    },

    // ---------------------
    // rStatus unchanged
    // ---------------------
    rStatus(requestId) {
      const role = this.requests.find(r => r.id === requestId)?.role;
      const related = this.candidates.filter(c => c.applied_role === role);
      const onboarded = related.filter(c => c.status === "Onboarding").length;
      return `${onboarded}/${related.length}`;
    },

    readableColumnName(key) {
      const map = {
        company_name: "Perusahaan",
        must_have_skill: "Kemampuan Wajib",
        request_candidate_id: "Request Candidate ID",
        test_date: "Tanggal Tes",
        motivation: "Motivasi",
        continue_next: "Lanjut?",
        final_result: "Hasil Akhir",
        no_telp: "HP/Telp",
        domisili: "Domisili",
        domain12_score: "Domain 1 & 2 Score",
        test_created_at: "Candidate Created At"
      };
      return map[key] || key.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase());
    },

    formatCellValue(key, value) {
      if (!value) return "—";

      const dateKeys = [
        "test_date","schedule_datetime","created_at","updated_at",
        "aptitude_date","technical_date","professional_date"
      ];

      if (dateKeys.includes(key)) {
        const d = new Date(value);
        if (!isNaN(d)) {
          return d.toLocaleDateString("id-ID", { day: "2-digit", month: "short", year: "numeric" });
        }
      }

      if (key === "motivation") {
        if (value === "green_flag") return "Green Flag";
        if (value === "red_flag") return "Red Flag";
      }

      return value;
    },

    getCellClass(key, value) {
      if (key === "motivation") {
        if (value === "green_flag") return "cell-green";
        if (value === "red_flag") return "cell-red";
      }
      if (key === "continue_next") {
        if (String(value).toLowerCase() === "ya") return "cell-green";
        if (String(value).toLowerCase() === "tidak") return "cell-red";
      }
      if (key === "final_result") {
        if (String(value).toLowerCase() === "lulus") return "cell-green";
        if (String(value).toLowerCase().includes("tidak")) return "cell-red";
      }
      return "";
    }
  }
};
</script>

<style scoped>
/* ===== TABLE SCROLL WRAPPER ===== */
.table-scroll-wrapper {
  width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  border-radius: 8px;
  -webkit-overflow-scrolling: touch;
  margin-top: 10px;
}

.table-scroll-wrapper::-webkit-scrollbar {
  height: 8px;
}

.table-scroll-wrapper::-webkit-scrollbar-thumb {
  background: #caa7a7;
  border-radius: 4px;
}

.table-scroll-wrapper::-webkit-scrollbar-thumb:hover {
  background: #a26060;
}

/* ===== DASHBOARD WRAPPER ===== */
.dashboard-wrapper {
  background: linear-gradient(180deg, #f9f3f3, #fff);
  min-height: 100vh;
  display: flex;
  justify-content: center;
  padding: 90px 0;
  box-sizing: border-box;
}

/* ===== DASHBOARD CONTAINER ===== */
.dashboard-container {
  width: 90%;
  max-width: 1200px;
  color: #333;
  font-family: "Poppins", sans-serif;
  display: flex;
  flex-direction: column;
  gap: 60px;
}

/* ===== HEADER ===== */
.dashboard-header {
  text-align: left;
}

.dashboard-header h1,
.dashboard-title {
  font-size: 32px;
  font-weight: 700;
  color: #7a3e3e;
  margin-bottom: 6px;
}

.title-underline {
  width: 80px;
  height: 4px;
  background: #a26060;
  border-radius: 5px;
}

/* ===== SUMMARY CARDS ===== */
.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 25px;
}

.card {
  background: #fff;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 6px 16px rgba(162, 96, 96, 0.15);
  border: 1px solid #f1e4e4;
  transition: all 0.3s ease;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 22px rgba(162, 96, 96, 0.25);
}

.card-content {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 15px;
}

.card-info {
  display: flex;
  flex-direction: column;
  justify-content: center;
  transform: translateY(6px);
}

.card-icon {
  background: #a26060;
  color: #fff;
  border-radius: 50%;
  width: 55px;
  height: 55px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  box-shadow: 0 3px 6px rgba(162, 96, 96, 0.25);
}

.card-info h3 {
  font-size: 15px;
  color: #7a3e3e;
  margin: 0;
}

.card-value {
  font-size: 22px;
  font-weight: 700;
  color: #000;
  margin-top: 4px;
}

/* ===== TABLE SECTION ===== */
.section-header h2,
.section h2 {
  font-size: 22px;
  font-weight: 700;
  color: #7a3e3e;
  border-left: 4px solid #a26060;
  padding-left: 10px;
  margin-bottom: 20px;
}

.request-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
  border-radius: 8px;
  overflow: hidden;
}

.request-table thead th {
  background-color: #a26060;
  color: #fff;
  text-align: center;
  padding: 12px;
  font-weight: 600;
}

.request-table tbody tr {
  background: #fff;
  border-bottom: 1px solid #eee;
  transition: background 0.2s;
}

.request-table tbody tr:hover {
  background: #f8f2f2;
}

.request-table td {
  padding: 12px;
  text-align: center;
}

/* ===== CELL COLORING ===== */
.cell-green {
  color: #0d8b1f;
  font-weight: 600;
}

.cell-red {
  color: #c20b0b;
  font-weight: 600;
}

.request-table td.cell-green {
  background-color: #e6f7ea;
}

.request-table td.cell-red {
  background-color: #fde8e8;
}

/* ===== CALENDAR SECTION ===== */
.calendar-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 25px;
  margin-top: 25px;
}

.calendar-card {
  display: flex;
  align-items: center;
  background: #fff;
  border-radius: 14px;
  padding: 15px;
  box-shadow: 0 4px 12px rgba(162, 96, 96, 0.1);
  border: 1px solid #f1e4e4;
  transition: all 0.3s ease;
}

.calendar-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 18px rgba(162, 96, 96, 0.2);
}

.calendar-date {
  background: #a26060;
  color: #fff;
  border-radius: 12px;
  width: 70px;
  height: 70px;
  text-align: center;
  display: flex;
  flex-direction: column;
  justify-content: center;
  margin-right: 15px;
  box-shadow: 0 3px 6px rgba(162, 96, 96, 0.25);
}

.calendar-day {
  font-size: 22px;
  font-weight: 700;
}

.calendar-month {
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.stage {
  font-size: 16px;
  font-weight: 700;
  color: #a26060;
  margin-bottom: 6px;
}

.candidate-name {
  font-size: 14px;
  color: #333;
}

.candidate-name i {
  color: #a26060;
  margin-right: 6px;
}

.no-schedule {
  text-align: center;
  color: #777;
  margin-top: 20px;
  font-size: 14px;
}

/* ===== PHASE BUTTONS ===== */
.phase-buttons {
  display: flex;
  gap: 10px;
  margin-bottom: 0; /* moved margin to .phase-header */
}

.phase-buttons button {
  background: #a26060;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: 0.3s;
  font-weight: 600;
}

.phase-buttons button:hover {
  background: #7a3e3e;
}

.phase-buttons button.active {
  background: #4a1e1e;
}

/* ===== PHASE HEADER (buttons + search) ===== */
.phase-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.phase-search {
  padding: 8px 14px;
  border: 1px solid #caa7a7;
  border-radius: 8px;
  width: 260px;
  font-size: 14px;
  outline: none;
  transition: 0.2s;
}

.phase-search:focus {
  border-color: #a26060;
  box-shadow: 0 0 4px rgba(162, 96, 96, 0.4);
}

/* ===== REQUESTS HEADER (title + search) ===== */
.requests-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.requests-title {
  font-weight: 700;
  color: #333;
}

.requests-search {
  padding: 8px 12px;
  border: 1px solid #caa7a7;
  border-radius: 8px;
  width: 220px;
  font-size: 14px;
  outline: none;
  transition: 0.2s;
}

.requests-search:focus {
  border-color: #a26060;
  box-shadow: 0 0 4px rgba(162, 96, 96, 0.4);
}

/* ===== PAGINATION ===== */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 15px;
  gap: 10px;
}

.pagination button {
  background: #a26060;
  color: white;
  border: none;
  padding: 6px 14px;
  border-radius: 6px;
  cursor: pointer;
  transition: 0.3s;
}

.pagination button:hover {
  background: #7a3e3e;
}

.pagination button:disabled {
  background: #caa7a7;
  cursor: not-allowed;
}

.status-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  text-transform: capitalize;
  color: white;
  min-width: 70px;
  text-align: center;
}

.status-badge.cell-green {
  background-color: #0c8c41; 
}

.status-badge.cell-red {
  background-color: #ab2929; 
}
</style>

