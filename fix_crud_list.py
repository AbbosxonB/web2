
import os

file_path = r'c:\Users\Alikhanovich\OneDrive\Ishchi stol\web2\templates\crud_list.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Define the markers
start_marker = "function renderForm(values = {}) {"
end_marker = "if (f.type === 'select') {"

# Find position of renderForm definition
start_idx = content.find(start_marker)
if start_idx == -1:
    print("Could not find start marker")
    exit(1)

# Find position of the select block (we expect it to be after start_marker)
# Note: There might be multiple select blocks or garbage.
# The one we want to resume at is the one that handles the select field rendering.
# In the BROKEN file, this appears after the garbage.
end_idx = content.find(end_marker, start_idx + len(start_marker))

if end_idx == -1:
    print("Could not find end marker")
    exit(1)

# The new content to insert
new_content = """function renderForm(values = {}) {
        const container = document.getElementById('modalFormContainer');
        container.innerHTML = config.fields.map(f => {
            let val = values[f.name] || '';
            // Datetime fix
            if (f.type === 'datetime-local' && val) val = val.slice(0, 16);

            if (f.type === 'permissions_matrix') {
                const existingPerms = values[f.name] || []; // Array of {module:..., can_view:...}
                
                const getChecked = (mod, action) => {
                    const found = existingPerms.find(p => p.module === mod);
                    return (found && found[`can_${action}`]) ? 'checked' : '';
                };

                const rows = f.modules.map(mod => `
                    <tr class="hover:bg-gray-50 border-b">
                        <td class="px-4 py-2 text-sm font-medium text-gray-700">${mod.text}</td>
                        <td class="px-4 py-2 text-center"><input type="checkbox" id="perm-${mod.val}-view" ${getChecked(mod.val, 'view')} class="w-4 h-4 text-blue-600 rounded"></td>
                        <td class="px-4 py-2 text-center"><input type="checkbox" id="perm-${mod.val}-update" ${getChecked(mod.val, 'update')} class="w-4 h-4 text-blue-600 rounded"></td>
                        <td class="px-4 py-2 text-center"><input type="checkbox" id="perm-${mod.val}-create" ${getChecked(mod.val, 'create')} class="w-4 h-4 text-blue-600 rounded"></td>
                        <td class="px-4 py-2 text-center"><input type="checkbox" id="perm-${mod.val}-delete" ${getChecked(mod.val, 'delete')} class="w-4 h-4 text-blue-600 rounded"></td>
                        <td class="px-4 py-2 text-center"><input type="checkbox" id="perm-${mod.val}-export" ${getChecked(mod.val, 'export')} class="w-4 h-4 text-blue-600 rounded"></td>
                        <td class="px-4 py-2 text-center"><input type="checkbox" onchange="toggleRow('${mod.val}', this.checked)" class="w-4 h-4 text-indigo-600 rounded"></td>
                    </tr>
                `).join('');

                return `
                <div class="mb-4 text-left">
                    <label class="block text-gray-700 text-sm font-bold mb-2">${f.label}</label>
                    <div class="overflow-x-auto border rounded-lg max-h-64 overflow-y-auto">
                        <table class="min-w-full divide-y divide-gray-200 head-fixed">
                            <thead class="bg-gray-100 sticky top-0 z-10">
                                <tr>
                                    <th class="px-4 py-2 text-left text-xs font-semibold text-gray-600 uppercase">Imkoniyatlar</th>
                                    <th class="px-4 py-2 text-center text-xs font-semibold text-gray-600 uppercase">View</th>
                                    <th class="px-4 py-2 text-center text-xs font-semibold text-gray-600 uppercase">Update</th>
                                    <th class="px-4 py-2 text-center text-xs font-semibold text-gray-600 uppercase">Create</th>
                                    <th class="px-4 py-2 text-center text-xs font-semibold text-gray-600 uppercase">Delete</th>
                                    <th class="px-4 py-2 text-center text-xs font-semibold text-gray-600 uppercase">Exp/Imp</th>
                                    <th class="px-4 py-2 text-center text-xs font-semibold text-gray-600 uppercase">All</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-200 bg-white">
                                ${rows}
                            </tbody>
                        </table>
                    </div>
                </div>`;
            }

            """

# Construct the final content
final_content = content[:start_idx] + new_content + content[end_idx:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(final_content)

print("File updated successfully")
