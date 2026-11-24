import "@testing-library/jest-dom";

if (!window.URL.createObjectURL) {
  window.URL.createObjectURL = jest.fn(() => "blob:preview");
}
