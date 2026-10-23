'use client';

import React, { useState, useMemo } from 'react';

// --- Mock Data Generation ---
// Generating 65 rows to demonstrate the 25-row pagination limit.
const generateMockData = () => {
  const data = [];
  const inches = ['55"', '65"', '77"', '83"'];
  const series = ['OLED Evo', 'QNED', 'UHD', 'NanoCell'];
  const socs = ['Alpha 9', 'Alpha 7', 'Alpha 5', 'MediaTek'];
  const regions = ['North America', 'Europe', 'Asia', 'Latin America'];
  const teams = ['QA Team A', 'QA Team B', 'Dev Team', 'Support'];

  for (let i = 1; i <= 65; i++) {
    const row: any = {
      id: i,
      inch: inches[Math.floor(Math.random() * inches.length)],
      series: series[Math.floor(Math.random() * series.length)],
      soc: socs[Math.floor(Math.random() * socs.length)],
      region: regions[Math.floor(Math.random() * regions.length)],
      team: teams[Math.floor(Math.random() * teams.length)],
    };
    // Generate the remaining columns up to 25 total columns
    for (let j = 7; j <= 25; j++) {
      row[`col${j}`] = `Data ${i}-${j}`;
    }
    data.push(row);
  }
  return data;
};

const mockData = generateMockData();

export default function MappingPage() {
  // --- State Management ---
  const [data] = useState(mockData);
  const [currentPage, setCurrentPage] = useState(1);
  const [filters, setFilters] = useState({
    inch: '',
    series: '',
    soc: '',
    region: '',
    team: '',
  });

  const rowsPerPage = 25;

  // --- Filtering Logic ---
  const filteredData = useMemo(() => {
    return data.filter((item) => {
      return (
        (filters.inch === '' || item.inch === filters.inch) &&
        (filters.series === '' || item.series === filters.series) &&
        (filters.soc === '' || item.soc === filters.soc) &&
        (filters.region === '' || item.region === filters.region) &&
        (filters.team === '' || item.team === filters.team)
      );
    });
  }, [data, filters]);

  // --- Pagination Logic ---
  const totalPages = Math.ceil(filteredData.length / rowsPerPage);
  const paginatedData = useMemo(() => {
    const startIndex = (currentPage - 1) * rowsPerPage;
    return filteredData.slice(startIndex, startIndex + rowsPerPage);
  }, [filteredData, currentPage]);

  // --- Handlers ---
  const handleFilterChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setFilters({ ...filters, [e.target.name]: e.target.value });
    setCurrentPage(1); // Reset to first page on filter change
  };

  const handleDownload = (format: 'csv' | 'excel') => {
    alert(`Exporting data to ${format.toUpperCase()}...`);
    // Implement actual CSV/Excel export logic here
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col font-sans">
      {/* --- Ribbon Navbar --- */}
      <div className="bg-white border-b shadow-sm sticky top-0 z-10">
        <div className="flex flex-wrap items-center p-3 gap-6 overflow-x-auto">
          
          {/* 1. Command Section */}
          <div className="flex flex-col border-r pr-6">
            <span className="text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wider">Command</span>
            <div className="flex gap-2">
              <button className="px-4 py-1.5 bg-blue-600 text-white text-sm font-medium rounded hover:bg-blue-700 transition-colors">Pull</button>
              <button className="px-4 py-1.5 bg-green-600 text-white text-sm font-medium rounded hover:bg-green-700 transition-colors">Run</button>
              <button className="px-4 py-1.5 bg-yellow-500 text-white text-sm font-medium rounded hover:bg-yellow-600 transition-colors">Check</button>
              <button className="px-4 py-1.5 bg-purple-600 text-white text-sm font-medium rounded hover:bg-purple-700 transition-colors">Adopt</button>
            </div>
          </div>

          {/* 2. Filtering Section */}
          <div className="flex flex-col border-r pr-6">
            <span className="text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wider">Filtering</span>
            <div className="flex gap-3">
              <select name="inch" value={filters.inch} onChange={handleFilterChange} className="border rounded px-2 py-1.5 text-sm bg-gray-50">
                <option value="">All Inches</option>
                <option value='55"'>55"</option>
                <option value='65"'>65"</option>
                <option value='77"'>77"</option>
                <option value='83"'>83"</option>
              </select>
              <select name="series" value={filters.series} onChange={handleFilterChange} className="border rounded px-2 py-1.5 text-sm bg-gray-50">
                <option value="">All Series</option>
                <option value="OLED Evo">OLED Evo</option>
                <option value="QNED">QNED</option>
                <option value="UHD">UHD</option>
                <option value="NanoCell">NanoCell</option>
              </select>
              <select name="soc" value={filters.soc} onChange={handleFilterChange} className="border rounded px-2 py-1.5 text-sm bg-gray-50">
                <option value="">All SoC</option>
                <option value="Alpha 9">Alpha 9</option>
                <option value="Alpha 7">Alpha 7</option>
                <option value="Alpha 5">Alpha 5</option>
                <option value="MediaTek">MediaTek</option>
              </select>
              <select name="region" value={filters.region} onChange={handleFilterChange} className="border rounded px-2 py-1.5 text-sm bg-gray-50">
                <option value="">All Regions</option>
                <option value="North America">North America</option>
                <option value="Europe">Europe</option>
                <option value="Asia">Asia</option>
                <option value="Latin America">Latin America</option>
              </select>
              <select name="team" value={filters.team} onChange={handleFilterChange} className="border rounded px-2 py-1.5 text-sm bg-gray-50">
                <option value="">All Teams</option>
                <option value="QA Team A">QA Team A</option>
                <option value="QA Team B">QA Team B</option>
                <option value="Dev Team">Dev Team</option>
                <option value="Support">Support</option>
              </select>
            </div>
          </div>

          {/* 3. Download Section */}
          <div className="flex flex-col">
            <span className="text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wider">Download</span>
            <div className="flex gap-2">
              <button onClick={() => handleDownload('csv')} className="px-4 py-1.5 bg-gray-800 text-white text-sm font-medium rounded hover:bg-gray-900 transition-colors">
                Export CSV
              </button>
              <button onClick={() => handleDownload('excel')} className="px-4 py-1.5 bg-emerald-600 text-white text-sm font-medium rounded hover:bg-emerald-700 transition-colors">
                Export Excel
              </button>
            </div>
          </div>

        </div>
      </div>

      {/* --- Table Section --- */}
      <div className="flex-1 p-4 overflow-hidden flex flex-col">
        <div className="bg-white border rounded shadow-sm flex-1 overflow-auto">
          <table className="min-w-max w-full text-left border-collapse">
            <thead className="bg-gray-100 sticky top-0 z-0 shadow-sm">
              <tr>
                <th className="px-4 py-3 border-b text-sm font-semibold text-gray-700">ID</th>
                <th className="px-4 py-3 border-b text-sm font-semibold text-gray-700">Inch</th>
                <th className="px-4 py-3 border-b text-sm font-semibold text-gray-700">Series</th>
                <th className="px-4 py-3 border-b text-sm font-semibold text-gray-700">SoC</th>
                <th className="px-4 py-3 border-b text-sm font-semibold text-gray-700">Region</th>
                <th className="px-4 py-3 border-b text-sm font-semibold text-gray-700">Team</th>
                {/* Render remaining 19 columns to make it 25 total */}
                {Array.from({ length: 19 }).map((_, idx) => (
                  <th key={idx} className="px-4 py-3 border-b text-sm font-semibold text-gray-700">
                    Column {idx + 7}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {paginatedData.length > 0 ? (
                paginatedData.map((row) => (
                  <tr key={row.id} className="hover:bg-gray-50 border-b last:border-none">
                    <td className="px-4 py-2 text-sm text-gray-600">{row.id}</td>
                    <td className="px-4 py-2 text-sm text-gray-600">{row.inch}</td>
                    <td className="px-4 py-2 text-sm text-gray-600">{row.series}</td>
                    <td className="px-4 py-2 text-sm text-gray-600">{row.soc}</td>
                    <td className="px-4 py-2 text-sm text-gray-600">{row.region}</td>
                    <td className="px-4 py-2 text-sm text-gray-600">{row.team}</td>
                    {Array.from({ length: 19 }).map((_, idx) => (
                      <td key={idx} className="px-4 py-2 text-sm text-gray-600">
                        {row[`col${idx + 7}`]}
                      </td>
                    ))}
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={25} className="px-4 py-8 text-center text-gray-500">
                    No data found matching the selected filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* --- Pagination Section --- */}
        <div className="mt-4 flex items-center justify-between bg-white p-3 border rounded shadow-sm">
          <div className="text-sm text-gray-600">
            Showing <span className="font-semibold">{(currentPage - 1) * rowsPerPage + 1}</span> to{' '}
            <span className="font-semibold">
              {Math.min(currentPage * rowsPerPage, filteredData.length)}
            </span>{' '}
            of <span className="font-semibold">{filteredData.length}</span> entries
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
              disabled={currentPage === 1}
              className="px-3 py-1.5 border rounded text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Previous
            </button>
            <span className="px-4 py-1.5 text-sm font-medium bg-gray-100 rounded">
              Page {currentPage} of {totalPages || 1}
            </span>
            <button
              onClick={() => setCurrentPage((prev) => Math.min(prev + 1, totalPages))}
              disabled={currentPage === totalPages || totalPages === 0}
              className="px-3 py-1.5 border rounded text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}