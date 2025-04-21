import pandas as pd
import numpy as np

# Pipe internal diameters (IOP) in mm
IOP = [96.8, 111.6, 125, 142.8, 160.8, 178.6, 201, 223.4, 250.4, 314.8,
       366, 416.4, 466.8, 518, 619.6, 313.2, 364.4, 414.6, 464.8, 516,
       617.4, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600,
       1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700,
       2800, 2900, 3000, 3100]


def calculate_velocity(discharge, diameter):
    """Calculate flow velocity in m/s"""
    return discharge * (4 / (np.pi * (diameter / 1000) ** 2))


def calculate_head_loss(length, discharge, diameter):
    """
    Calculate friction head loss with 10% fitting loss
    Using modified Hazen-Williams formula (since C=1)
    """
    return (length * (discharge) ** 1.81) / (994.62 * (diameter / 1000) ** 4.81) * 1.1


def calculate_residual_head(delta_elevation, start_head, head_loss):
    """Calculate residual head at pipe end"""
    return (delta_elevation + start_head) - head_loss


def find_optimal_pipe(row, start_head):
    """Find the smallest pipe that meets velocity and pressure requirements"""
    is_village = "V" in str(row['end_node'])

    for diameter in sorted(IOP):  # Try from smallest to largest
        velocity = calculate_velocity(row['discharge'], diameter)
        head_loss = calculate_head_loss(row['length'], row['discharge'], diameter)
        end_head = calculate_residual_head(
            row['ground_level_start'] - row['ground_level_end'],
            start_head,
            head_loss
        )

        # Check constraints
        velocity_ok = 0.6 < velocity < 3
        pressure_ok = (not is_village) or (end_head >= 28)

        if velocity_ok and pressure_ok:
            return {
                'diameter': diameter,
                'velocity': velocity,
                'head_loss': head_loss,
                'start_head': start_head,
                'end_head': end_head
            }

    # If no pipe meets requirements, use largest available
    diameter = max(IOP)
    velocity = calculate_velocity(row['discharge'], diameter)
    head_loss = calculate_head_loss(row['length'], row['discharge'], diameter)
    end_head = calculate_residual_head(
        row['ground_level_start'] - row['ground_level_end'],
        start_head,
        head_loss
    )

    return {
        'diameter': diameter,
        'velocity': velocity,
        'head_loss': head_loss,
        'start_head': start_head,
        'end_head': end_head
    }


def process_network(df):
    """Process entire pipe network sequentially"""
    results = []
    previous_end_head = 0  # Initial residual head

    for _, row in df.iterrows():
        result = find_optimal_pipe(row, previous_end_head)
        results.append(result)
        previous_end_head = result['end_head']

    # Add results to dataframe
    result_df = df.copy()
    for i, col in enumerate(['diameter', 'velocity', 'head_loss', 'start_head', 'end_head']):
        result_df[col] = [r[col] for r in results]

    return result_df


# Main execution
if __name__ == "__main__":
    # Load data
    df = pd.read_excel("ha.xlsx", sheet_name="Sheet1")

    # Process network
    result_df = process_network(df)

    # Save results
    result_df.to_excel('mha_optimized.xlsx', index=False)

    # Generate validation report
    village_nodes = result_df[result_df['end_node'].str.contains('V', na=False)]
    validation_report = {
        'velocity_violations': result_df[(result_df['velocity'] <= 0.6) | (result_df['velocity'] >= 3)],
        'pressure_violations': village_nodes[village_nodes['end_head'] < 28]
    }

    print(f"Validation Report:\n"
          f"Pipes with velocity violations: {len(validation_report['velocity_violations'])}\n")
          # f"Village nodes with pressure violations: {len(validation_report['pressure_violations']}")