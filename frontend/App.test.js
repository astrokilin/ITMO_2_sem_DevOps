import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import App from "./app";

// мокаем fetch
beforeEach(() => {
  global.fetch = jest.fn((url, options) => {
    if (!options) {
      // GET
      return Promise.resolve({
        json: () => Promise.resolve([{ _id: "1", title: "Test", content: "Note" }]),
      });
    }

    if (options.method === "POST") {
      return Promise.resolve({
        json: () => Promise.resolve({ _id: "2", title: "New", content: "Content" }),
      });
    }

    if (options.method === "PUT") {
      return Promise.resolve({
        json: () => Promise.resolve({ _id: "1", title: "Updated", content: "Note" }),
      });
    }

    if (options.method === "DELETE") {
      return Promise.resolve({});
    }
  });
});

afterEach(() => {
  jest.clearAllMocks();
});

test("загрузка заметок при старте", async () => {
  render(<App />);
  expect(await screen.findByText("Test")).toBeInTheDocument();
});

test("создание заметки", async () => {
  render(<App />);

  await userEvent.type(screen.getByPlaceholderText("Заголовок"), "New");
  await userEvent.type(screen.getByPlaceholderText("Содержание"), "Content");

  await userEvent.click(screen.getByRole("button", { name: "Создать" }));

  expect(await screen.findByText("New")).toBeInTheDocument();
});

test("редактирование заметки", async () => {
  render(<App />);
  expect(await screen.findByText("Test")).toBeInTheDocument();

  await userEvent.click(screen.getByRole("button", { name: "Редактировать" }));

  const input = screen.getByDisplayValue("Test");
  await userEvent.clear(input);
  await userEvent.type(input, "Updated");

  await userEvent.click(screen.getByRole("button", { name: "Сохранить" }));

  expect(await screen.findByText("Updated")).toBeInTheDocument();
});

test("удаление заметки", async () => {
  render(<App />);
  expect(await screen.findByText("Test")).toBeInTheDocument();

  await userEvent.click(screen.getByRole("button", { name: "Удалить" }));

  await waitFor(() => {
    expect(screen.queryByText("Test")).not.toBeInTheDocument();
  });
});

test("отмена редактирования", async () => {
  render(<App />);
  expect(await screen.findByText("Test")).toBeInTheDocument();

  await userEvent.click(screen.getByRole("button", { name: "Редактировать" }));
  await userEvent.click(screen.getByRole("button", { name: "Отмена" }));

  expect(screen.getByText("Test")).toBeInTheDocument();
});

test("флажок Telegram работает", async () => {
  render(<App />);
  const checkbox = screen.getByRole("checkbox", { name: /telegram/i });

  expect(checkbox).not.toBeChecked();
  await userEvent.click(checkbox);
  expect(checkbox).toBeChecked();
});

