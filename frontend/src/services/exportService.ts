import { apiClient } from "@/services/apiClient";

type Schedule = "fsi" | "a3";

function triggerDownload(blob: Blob, filename: string) {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

export const exportService = {
  downloadCsv: async (sessionId: string, schedule: Schedule) => {
    const { data } = await apiClient.get<Blob>("/export/csv", {
      params: { session_id: sessionId, schedule },
      responseType: "blob",
    });
    triggerDownload(data, `schedule_${schedule}_${sessionId}.csv`);
  },

  downloadPdf: async (sessionId: string) => {
    const { data } = await apiClient.get<Blob>("/export/pdf", {
      params: { session_id: sessionId },
      responseType: "blob",
    });
    triggerDownload(data, `itr_foreign_report_${sessionId}.pdf`);
  },
};
