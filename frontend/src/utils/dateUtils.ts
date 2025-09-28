/**
 * Utility functions for date calculations
 * All calendar calculations use New York timezone for financial data consistency
 */

/**
 * Gets the current date in New York timezone
 * @returns Date object representing current date in NY timezone
 */
function getNYDate(): Date {
  const now = new Date();
  // Convert to NY timezone (UTC-5 for EST, UTC-4 for EDT)
  // We'll use a simple approach: check if we're in daylight saving time
  const isDST = isDaylightSavingTime(now);
  const nyOffset = isDST ? -4 : -5; // EDT or EST
  
  const utc = now.getTime() + (now.getTimezoneOffset() * 60000);
  const nyTime = new Date(utc + (nyOffset * 3600000));
  
  // Return only the date part (no time) to match backend behavior
  const dateOnly = new Date(nyTime.getFullYear(), nyTime.getMonth(), nyTime.getDate());
  return dateOnly;
}

/**
 * Simple daylight saving time check for US Eastern timezone
 * DST starts on second Sunday of March and ends on first Sunday of November
 */
function isDaylightSavingTime(date: Date): boolean {
  const year = date.getFullYear();
  
  // DST starts on second Sunday of March
  const marchDST = getSecondSundayOfMarch(year);
  
  // DST ends on first Sunday of November
  const novemberDST = getFirstSundayOfNovember(year);
  
  return date >= marchDST && date < novemberDST;
}

function getSecondSundayOfMarch(year: number): Date {
  const march1 = new Date(year, 2, 1); // March 1st
  const firstSunday = new Date(march1.getTime());
  firstSunday.setDate(1 + (7 - march1.getDay()) % 7);
  const secondSunday = new Date(firstSunday.getTime());
  secondSunday.setDate(firstSunday.getDate() + 7);
  return secondSunday;
}

function getFirstSundayOfNovember(year: number): Date {
  const november1 = new Date(year, 10, 1); // November 1st
  const firstSunday = new Date(november1.getTime());
  firstSunday.setDate(1 + (7 - november1.getDay()) % 7);
  return firstSunday;
}

/**
 * Gets the previous working day (Monday-Friday) from a given date
 * @param date - The reference date (defaults to current NY date)
 * @returns The previous working day as a Date object
 */
export function getPreviousWorkingDay(date: Date = getNYDate()): Date {
  const result = new Date(date.getTime());
  
  // Go back one day
  result.setDate(result.getDate() - 1);
  
  // If it's Saturday (6) or Sunday (0), go back to Friday
  if (result.getDay() === 0) { // Sunday
    result.setDate(result.getDate() - 2); // Go back to Friday
  } else if (result.getDay() === 6) { // Saturday
    result.setDate(result.getDate() - 1); // Go back to Friday
  }
  
  return result;
}

/**
 * Checks if a given date is after the previous working day
 * @param year - Year to check
 * @param month - Month to check (0-based)
 * @param day - Day to check
 * @param referenceDate - The reference date to calculate previous working day from (defaults to current NY date)
 * @returns True if the date is after the previous working day
 */
export function isDateAfterPreviousWorkingDay(year: number, month: number, day: number, referenceDate: Date = getNYDate()): boolean {
  const date = new Date(year, month, day);
  const previousWorkingDay = getPreviousWorkingDay(referenceDate);
  
  // Set both dates to end of day for comparison
  date.setHours(23, 59, 59, 999);
  previousWorkingDay.setHours(23, 59, 59, 999);
  
  return date > previousWorkingDay;
}

/**
 * Gets the previous working day as a string in YYYY-MM-DD format
 * @param date - The reference date (defaults to current NY date)
 * @returns The previous working day as a string
 */
export function getPreviousWorkingDayString(date: Date = getNYDate()): string {
  const previousWorkingDay = getPreviousWorkingDay(date);
  return previousWorkingDay.toISOString().split('T')[0];
}
