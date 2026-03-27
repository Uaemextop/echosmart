/**
 * EchoSmart Demo — Users Page Renderer
 */

const USERS = [
  { name: "John Doe",       email: "john@echosmart.io",  role: "Admin",    status: "online",  initials: "JD" },
  { name: "María García",   email: "maria@echosmart.io", role: "Operador", status: "online",  initials: "MG" },
  { name: "Carlos López",   email: "carlos@echosmart.io",role: "Visor",    status: "offline", initials: "CL" },
  { name: "Ana Martínez",   email: "ana@echosmart.io",   role: "Operador", status: "online",  initials: "AM" },
];

export function renderUsers() {
  const tbody = document.getElementById("usersTableBody");
  if (!tbody) return;

  tbody.innerHTML = USERS.map((u) => `
    <tr>
      <td>
        <div class="user-row__info">
          <div class="sidebar__avatar">${u.initials}</div>
          <span>${u.name}</span>
        </div>
      </td>
      <td>${u.email}</td>
      <td>${u.role}</td>
      <td><span class="status-dot status-dot--${u.status}"></span> ${u.status === "online" ? "Activo" : "Inactivo"}</td>
    </tr>
  `).join("");
}
