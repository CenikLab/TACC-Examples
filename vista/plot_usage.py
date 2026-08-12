#!/usr/bin/env python3
"""Plot SLURM usage by month from sacct output files."""

from __future__ import annotations

import argparse
import math
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np


# Fill in your actual multipliers here.
PARTITION_MULTIPLIERS: Dict[str, float] = {
	"gh": 1.0,
	"gh-dev": 1.0,
	"gg": 1.0/3.0,
}

DEFAULT_PARTITION_MULTIPLIER = 1.0
ROUND_MINUTES = 15


def parse_elapsed_minutes(value: str) -> Optional[float]:
	"""Parse sacct elapsed time into minutes.

	Accepts formats like HH:MM:SS or DD-HH:MM:SS.
	"""
	if not value or value in {"None", "Unknown"}:
		return None

	parts = value.split("-")
	if len(parts) == 2:
		day_part, time_part = parts
		try:
			days = int(day_part)
		except ValueError:
			return None
	else:
		days = 0
		time_part = parts[0]

	time_bits = time_part.split(":")
	if len(time_bits) == 3:
		hours_str, minutes_str, seconds_str = time_bits
	elif len(time_bits) == 2:
		hours_str, minutes_str = "0", time_bits[0]
		seconds_str = time_bits[1]
	else:
		return None

	try:
		hours = int(hours_str)
		minutes = int(minutes_str)
		seconds = int(seconds_str)
	except ValueError:
		return None

	total_seconds = days * 86400 + hours * 3600 + minutes * 60 + seconds
	return total_seconds / 60.0


def ceil_minutes(minutes: float, interval: int) -> float:
	if minutes <= 0:
		return 0.0
	return math.ceil(minutes / interval) * interval


def parse_start_time(value: str) -> Optional[datetime]:
	if not value or value in {"None", "Unknown"}:
		return None
	try:
		return datetime.fromisoformat(value)
	except ValueError:
		return None


def safe_int(value: str) -> int:
	try:
		return int(value)
	except (TypeError, ValueError):
		return 0


def is_header_row(parts: List[str]) -> bool:
	return "JobID" in parts and "Elapsed" in parts


def parse_sacct_file(path: Path, jobs: Dict[str, dict]) -> None:
	header: Optional[List[str]] = None
	col_idx: Dict[str, int] = {}

	with path.open("r", encoding="utf-8") as handle:
		for line in handle:
			line = line.strip()
			if not line:
				continue
			if set(line) <= {"-"}:
				continue
			if re.match(r"^-{3,}$", line.replace(" ", "")):
				continue

			parts = re.split(r"\s+", line)
			if header is None or is_header_row(parts):
				header = parts
				col_idx = {name: idx for idx, name in enumerate(header)}
				continue

			if header is None:
				continue

			if len(parts) < len(header):
				parts.extend([""] * (len(header) - len(parts)))

			def get(col: str) -> str:
				idx = col_idx.get(col)
				if idx is None or idx >= len(parts):
					return ""
				return parts[idx]

			job_id = get("JobID")
			if not job_id:
				continue
			base_job_id = job_id.split(".")[0]

			elapsed_minutes = parse_elapsed_minutes(get("Elapsed"))
			n_nodes = safe_int(get("NNodes"))
			start_dt = parse_start_time(get("Start"))
			partition = get("Partition").strip() or None
			user = get("User").strip() or None

			entry = jobs.setdefault(
				base_job_id,
				{
					"elapsed_minutes": 0.0,
					"n_nodes": 0,
					"start": None,
					"partition": None,
					"user": None,
				},
			)

			if elapsed_minutes is not None:
				entry["elapsed_minutes"] = max(entry["elapsed_minutes"], elapsed_minutes)
			if n_nodes > 0:
				entry["n_nodes"] = max(entry["n_nodes"], n_nodes)
			if start_dt is not None:
				if entry["start"] is None or start_dt < entry["start"]:
					entry["start"] = start_dt
			if partition and entry["partition"] is None:
				entry["partition"] = partition
			if user and entry["user"] is None:
				entry["user"] = user


def month_range(start: datetime, end: datetime) -> List[datetime]:
	current = datetime(start.year, start.month, 1)
	last = datetime(end.year, end.month, 1)
	months = []
	while current <= last:
		months.append(current)
		year = current.year + (current.month // 12)
		month = (current.month % 12) + 1
		current = datetime(year, month, 1)
	return months


def aggregate_usage(jobs: Dict[str, dict]) -> Tuple[List[str], Dict[str, Dict[str, float]]]:
	usage = defaultdict(lambda: defaultdict(float))
	month_keys = []

	for job in jobs.values():
		if not job["start"]:
			continue
		if job["elapsed_minutes"] <= 0 or job["n_nodes"] <= 0:
			continue

		month_key = job["start"].strftime("%Y-%m")
		month_keys.append(job["start"])

		partition = (job["partition"] or "").strip()
		multiplier = PARTITION_MULTIPLIERS.get(
			partition,
			DEFAULT_PARTITION_MULTIPLIER,
		)
		rounded_minutes = ceil_minutes(job["elapsed_minutes"], ROUND_MINUTES)
		elapsed_hours = rounded_minutes / 60.0
		su = multiplier * job["n_nodes"] * elapsed_hours

		user = job["user"] or "unknown"
		usage[month_key][user] += su

	if not month_keys:
		return [], usage

	months = month_range(min(month_keys), max(month_keys))
	month_labels = [dt.strftime("%Y-%m") for dt in months]
	return month_labels, usage


def plot_usage(months: List[str], usage: Dict[str, Dict[str, float]], out_path: Optional[Path]) -> None:
	if not months:
		raise ValueError("No usage data found.")

	users = sorted(
		{user for month in usage.values() for user in month.keys()},
		key=lambda u: sum(usage[m].get(u, 0.0) for m in months),
		reverse=True,
	)

	x = np.arange(len(months))
	bottom = np.zeros(len(months))
	colors = plt.cm.tab20(np.linspace(0, 1, max(len(users), 1)))

	fig, ax = plt.subplots(figsize=(12, 6))
	for idx, user in enumerate(users):
		values = np.array([usage[m].get(user, 0.0) for m in months])
		ax.bar(x, values, bottom=bottom, label=user, color=colors[idx])
		bottom += values

	totals = bottom.copy()
	for i, month in enumerate(months):
		month_usage = usage.get(month, {})
		total = totals[i]
		if total <= 0:
			continue
		lines = [f"Total {total:.1f}"]
		for user in users:
			value = month_usage.get(user, 0.0)
			if value > 0:
				lines.append(f"{user} {value:.1f}")
		ax.text(
			x[i],
			total,
			"\n".join(lines),
			ha="center",
			va="bottom",
			fontsize=7,
		)

	if totals.size and totals.max() > 0:
		ax.set_ylim(top=totals.max() * 1.25)

	ax.set_xlabel("Month")
	ax.set_ylabel("Total SUs")
	ax.set_title("SLURM Usage by Month")
	ax.set_xticks(x, months, rotation=45, ha="right")
	ax.grid(axis="y", alpha=0.3)
	ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1), borderaxespad=0)
	fig.tight_layout()

	if out_path:
		fig.savefig(out_path, dpi=200)
	else:
		plt.show()


def main() -> None:
	parser = argparse.ArgumentParser(
		description="Plot SLURM usage by month from sacct output files.",
	)
	parser.add_argument(
		"files",
		nargs="+",
		help="One or more sacct output files.",
	)
	parser.add_argument(
		"--out",
		type=Path,
		default=None,
		help="Optional output image path. If omitted, show the plot.",
	)
	args = parser.parse_args()

	jobs: Dict[str, dict] = {}
	for file_path in args.files:
		parse_sacct_file(Path(file_path), jobs)

	months, usage = aggregate_usage(jobs)
	plot_usage(months, usage, args.out)


if __name__ == "__main__":
	main()
