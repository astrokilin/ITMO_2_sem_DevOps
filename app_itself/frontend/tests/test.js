window.testResults = [];

function assertEqual(actual, expected, message) {
    const passed = actual === expected;
    window.testResults.push({ name: message, passed, actual, expected });
}

function toggleEdit(note_id, toEdit) {
    const view = document.getElementById(`view-${note_id}`);
    const edit = document.getElementById(`edit-${note_id}`);
    if (toEdit) {
        view.style.display = 'none';
        edit.style.display = 'block';
    } else {
        view.style.display = 'block';
        edit.style.display = 'none';
    }
}

function testToggleEdit() {
    const noteId = "1";

    const view = document.createElement('div');
    view.id = `view-${noteId}`;
    view.style.display = 'block';

    const edit = document.createElement('div');
    edit.id = `edit-${noteId}`;
    edit.style.display = 'none';

    document.body.appendChild(view);
    document.body.appendChild(edit);

    toggleEdit(noteId, true);
    assertEqual(view.style.display, 'none', 'View hidden on edit');
    assertEqual(edit.style.display, 'block', 'Edit shown on edit');

    toggleEdit(noteId, false);
    assertEqual(view.style.display, 'block', 'View shown after cancel edit');
    assertEqual(edit.style.display, 'none', 'Edit hidden after cancel edit');

    document.body.removeChild(view);
    document.body.removeChild(edit);
}

testToggleEdit();

